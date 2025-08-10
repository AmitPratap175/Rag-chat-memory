from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from . import models

def get_random_questions(db: Session, limit: int = 10):
    return db.query(models.Question).order_by(func.random()).limit(limit).all()

def get_stats(db: Session):
    num_passages = db.query(models.Passage).count()
    num_questions = db.query(models.Question).count()
    return {"num_passages": num_passages, "num_questions": num_questions}

def get_questions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Question).offset(skip).limit(limit).all()

def update_question(db: Session, question_id: int, updated_question: dict):
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        return None

    for key, value in updated_question.items():
        setattr(question, key, value)

    db.commit()
    db.refresh(question)
    return question

def delete_question(db: Session, question_id: int):
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        return None

    db.delete(question)
    db.commit()
    return {"message": "Question deleted successfully"}

def check_answer(db: Session, question_id: int, answer: str):
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        return None

    correct_option = question.json_payload.get("correct_option")
    is_correct = correct_option.lower() == answer.lower()

    return {
        "is_correct": is_correct,
        "explanation": question.json_payload.get("explanation")
    }
