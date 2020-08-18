import os
import queue
import sqlite3
import sys
import traceback

from engineio.async_drivers import gevent
from flask import Flask, jsonify, request, g, session, json
from flask_socketio import SocketIO, emit, send
import database
from game_protocol import *
from game_service import Game, Gamer

app = Flask(__name__)
app.secret_key = os.urandom(42)
socketio = SocketIO(app, logger=False)


def gen_response(content=None, error=None, code=200):
    if content is None:
        content = {}
    content.update({"error": error, "is_ok": True if code == 200 else False})
    return jsonify(content), code


@app.errorhandler(sqlite3.DatabaseError)
def handle_database_error(e):
    if isinstance(e, sqlite3.IntegrityError):
        return gen_response(error=str(e), code=400)

    return gen_response(error=str(e), code=500)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/register', methods=['POST'])
def register():
    if not request.is_json:
        return gen_response(error="Body should contains JSON", code=400)

    if "user_name" not in request.json:
        return gen_response(error="Invalid request parameters", code=400)

    user_id = database.query_db("""insert into users(user_name) values(?)""", (request.json["user_name"],), ret_lastrowid=True)
    return gen_response({"user_id": user_id})


@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return gen_response(error="Body should contains JSON", code=400)

    if "user_name" not in request.json:
        return gen_response(error="Invalid request parameters", code=400)

    count = database.query_db("""select count() from users where user_name=?""", (request.json["user_name"],))[0]['count()']
    if count == 1:
        session["is_authorized"] = True
        return gen_response()
    else:
        return gen_response(error="Unknown user", code=403)


waiting_opponent = queue.Queue()
game_data = {}


def game_socket_finish(gamer1_data, gamer2_data):
    is_1_win = gamer1_data[2].is_win()

    send(message_end(is_1_win), namespace='/game', room=gamer2_data[0])
    send(message_end(not is_1_win), namespace='/game', room=gamer1_data[0])

    game_data.pop(gamer1_data[0])
    game_data.pop(gamer2_data[0])


@socketio.on_error('/game')
def error_handler_chat(e):
    if isinstance(e, NoMoreQuestionsException):
        game_socket_finish(e.gamer_data, game_data[e.gamer_data[0]])
        send(message_error(500, str(e)))
    else:
        traceback.print_tb(e.__traceback__)
        print(type(e).__name__ + ": " + str(e), file=sys.stderr)
        send(message_error(500, type(e).__name__ + ": " + str(e)))


class NoMoreQuestionsException(Exception):
    def __init__(self, gamer_data, message="No more questions :("):
        super().__init__(message)
        self.gamer_data = gamer_data


def game_socket_next_question(gamer_data):
    question = gamer_data[1].next_question(gamer_data[2])
    if question is None:
        raise NoMoreQuestionsException(gamer_data)
    else:
        message = message_question(question.ru_word, question.answers)

    socketio.send(message, namespace='/game', room=gamer_data[0])


@socketio.on('connect', namespace='/game')
def game_socket_connect():
    print("connect %s" % request.sid)
    # if not session.get("is_authorized", False):
    #     send(message_error(401, "Unauthorized connection"), namespace='/game')
    #     emit('disconnect', namespace='/game')
    #     return

    if waiting_opponent.empty():
        game_data[request.sid] = [None, Game(), Gamer()]
        waiting_opponent.put(request.sid, block=False)
    else:
        opponent = waiting_opponent.get()
        gamer1_data = game_data[opponent]
        gamer1_data[0] = request.sid
        gamer2_data = [opponent, gamer1_data[1], Gamer()]
        game_data[request.sid] = gamer2_data

        socketio.send(message_start(), namespace='/game', room=opponent)
        socketio.send(message_start(), namespace='/game', room=request.sid)

        game_socket_next_question(gamer1_data)
        game_socket_next_question(gamer2_data)


@socketio.on('message', namespace='/game')
def game_socket_message(message):
    # print('received: ' + str(message))
    if 'code' not in message:
        send(message_error(400, "Request should contains 'code' field"))
        return

    code = MessageCode(message['code'])
    if code == MessageCode.ANSWER:
        if 'answer_idx' not in message:
            send(message_error(400, "Request should contains 'answer_idx' field"))
            return

        gamer_data = game_data.get(request.sid, None)
        if gamer_data is None:
            send(message_error(404, "Game was end or not start yet"))
            return

        is_right = gamer_data[2].answer(message['answer_idx'])
        right_answer_idx = gamer_data[2].current_question.right_answer_idx
        send(message_answer_validation(right_answer_idx, is_right))

        if is_right:
            if gamer_data[2].is_win():
                game_socket_finish(gamer_data, game_data[gamer_data[0]])
                return
            else:
                opponent_answers_count = game_data[gamer_data[0]][2].right_answers_count
                send(message_progress(gamer_data[2].right_answers_count, opponent_answers_count), namespace='/game', room=request.sid)
                send(message_progress(opponent_answers_count, gamer_data[2].right_answers_count), namespace='/game', room=gamer_data[0])

        game_socket_next_question(gamer_data)


@socketio.on('disconnect', namespace='/game')
def game_socket_disconnect():
    print('disconnect %s' % request.sid)
    game_data.pop(request.sid, None)
    pass


if __name__ == '__main__':
    database.create_db_if_not_exist()
    socketio.run(app, debug=True, host='0.0.0.0', port=80)
