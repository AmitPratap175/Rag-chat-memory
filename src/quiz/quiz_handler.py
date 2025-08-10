from . import crud
from .database import SessionLocal

class QuizManager:
    def __init__(self, user_uuid):
        self.user_uuid = user_uuid
        self.db = SessionLocal()
        self.quiz = None
        self.current_question_index = 0

    def start_quiz(self, limit: int = 10):
        self.quiz = crud.get_random_questions(self.db, limit=limit)
        self.current_question_index = 0
        return self.get_current_question()

    def get_current_question(self):
        if self.quiz and self.current_question_index < len(self.quiz):
            return self.quiz[self.current_question_index]
        return None

    def get_next_question(self):
        self.current_question_index += 1
        return self.get_current_question()

    def check_answer(self, question_id: int, answer: str):
        return crud.check_answer(self.db, question_id, answer)

    def close(self):
        self.db.close()
