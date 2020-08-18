import random
from random import Random

import database


class Gamer:
    def __init__(self):
        self.current_question_idx = -1
        self.current_question = None
        self.right_answers_count = 0
        self.is_answered = False

    def is_win(self):
        return self.right_answers_count >= 10

    def set_next_question(self, question, idx):
        self.is_answered = False
        self.current_question_idx = idx
        self.current_question = question

    def answer(self, answer_idx):
        is_right = self.current_question.right_answer_idx == answer_idx

        if self.is_answered:
            raise Exception("dich error")
            return is_right

        if is_right and not self.is_answered:
            self.right_answers_count = self.right_answers_count + 1
            self.is_answered = True

        return is_right


class Question:
    def __init__(self, ru_word, answers, right_answer_idx):
        self.ru_word = ru_word
        self.answers = answers
        self.right_answer_idx = right_answer_idx


class Game:
    def __init__(self):
        self.curr_word_id = None
        self.used_word_ids = list()
        self.questions = list()
        self.gamers = set()

    def next_question(self, gamer):
        question_idx = gamer.current_question_idx + 1
        if question_idx < len(self.questions):
            gamer.set_next_question(self.questions[question_idx], question_idx)
            return self.questions[question_idx]

        placeholders = ', '.join(['?'] * len(self.used_word_ids))
        next_words = database.query_db("""select * from translates where word_id not in({}) order by random() limit 1""".format(placeholders), tuple(self.used_word_ids))
        if len(next_words) == 0:
            return None
        next_word = next_words[0]
        answers = database.query_db("""select * from translates where word_id not in(?) order by random() limit 4""", (next_word["word_id"],))
        # right_answer_idx = random.randint(0, len(answers))
        answers = [answer["en_word"] for answer in answers]
        right_answer_idx = random.randint(0, 4)
        answers.insert(right_answer_idx, next_word["en_word"])
        question = Question(next_word["ru_word"], answers, right_answer_idx)

        self.curr_word_id = next_word["word_id"]
        self.used_word_ids.append(self.curr_word_id)
        self.questions.append(question)

        gamer.set_next_question(question, len(self.questions))

        return question
