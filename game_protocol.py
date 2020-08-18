from enum import Enum


class MessageCode(Enum):
    START = "START"
    PROGRESS = "PROGRESS"
    ANSWER = "ANSWER"
    ANSWER_VALIDATION = "ANSWER_VALIDATION"
    QUESTION = "QUESTION"
    END = "END"
    ERROR = "ERROR"

    def __str__(self):
        return self.value


def message_start():
    return {"code": str(MessageCode.START)}


def message_progress(right_answers_count, opponent_right_answers_count):
    return {"code": str(MessageCode.PROGRESS),
            "right_answers_count": right_answers_count,
            "opponent_right_answers_count": opponent_right_answers_count}


def message_answer(answer_idx):
    return {"code": str(MessageCode.ANSWER), "answer_idx": answer_idx}


def message_answer_validation(right_answer_idx, is_right):
    return {"code": str(MessageCode.ANSWER_VALIDATION), "right_answer_idx": right_answer_idx, "is_right": is_right}


def message_question(word, translates):
    return {"code": str(MessageCode.QUESTION), "word": word, "translates": translates}


def message_end(is_win):
    return {"code": str(MessageCode.END), "is_win": is_win}


def message_error(code, msg=None):
    return {"code": str(MessageCode.ERROR), "http_code": code, "message": msg}
