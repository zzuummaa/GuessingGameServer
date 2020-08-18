import socketio
from game_protocol import MessageCode, message_answer

is_disconnected = False
socketIO = socketio.Client(logger=False, reconnection=False)


@socketIO.on('connect', namespace='/game')
def connect():
    print("I'm connected!")


@socketIO.event(namespace='/game')
def message(data):
    global is_disconnected
    print('receive: ' + str(data))
    if data['code'] == str(MessageCode.QUESTION):
        socketIO.send(message_answer(4), namespace='/game')
    elif data['code'] == str(MessageCode.ERROR):
        socketIO.disconnect()
        is_disconnected = True
    elif data['code'] == str(MessageCode.END):
        is_disconnected = True


@socketIO.on('disconnect', namespace='/game')
def disconnect():
    global is_disconnected
    print("I'm disconnected!")
    is_disconnected = True


socketIO.connect("http://localhost:80",
                 namespaces=['/game'],
                 headers={'cookie': 'session=eyJpc19hdXRob3JpemVkIjp0cnVlfQ.XzuX8g.PD1oByZQJA_SdgB1JsyC-5Rr9SY; HttpOnly; Path=/'})
while not is_disconnected:
    socketIO.sleep(1)
socketIO.disconnect()
