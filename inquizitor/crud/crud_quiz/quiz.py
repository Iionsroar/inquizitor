import logging
import random
import string
from pprint import pformat
from sqlmodel import Session
from typing import List, Union

from fastapi.encoders import jsonable_encoder

from inquizitor import crud, models
from inquizitor.crud.base import CRUDBase
from inquizitor.models import Quiz, QuizCreate, QuizUpdate


class CRUDQuiz(CRUDBase[Quiz, QuizCreate, QuizUpdate]):
    def create(self, db: Session, *, obj_in: QuizCreate) -> Quiz:
        db_obj = Quiz(
            name=obj_in.name,
            desc=obj_in.desc,
            number_of_questions=obj_in.number_of_questions,
            created_at=obj_in.created_at,
            due_date=obj_in.due_date,
            quiz_code=self.generate_code(db),
            teacher_id=obj_in.teacher_id,
        )
        return super().create(db, obj_in=db_obj)

    def generate_code(self, db: Session) -> str:
        """Generate random characters for quiz_code"""
        while True:
            characters = string.ascii_letters + string.digits
            quiz_code = "".join(random.choice(characters) for i in range(6))
            # check if generated quiz_code already exists
            existing_code = db.query(Quiz).filter(Quiz.quiz_code == quiz_code).first()
            if not existing_code:
                break
        return quiz_code

    def get_by_code(self, db: Session, code: str) -> Quiz:
        """Read quiz by quiz_code"""
        return db.query(Quiz).filter(Quiz.quiz_code == code).first()

    def get_by_index(self, db: Session, quiz_index: Union[int, str]) -> Quiz:
        """Read quiz by quiz_code or int"""
        if isinstance(quiz_index, str):
            quiz = self.get_by_code(db, code=quiz_index)
        else:
            quiz = self.get(db, id=quiz_index)
        return quiz

    def get_multi_by_name(
        self, db: Session, *, name: str, skip: int = 0, limit: int = 100
    ) -> List[Quiz]:
        """Read quizzes by name attribute only (not unique)"""
        return db.query(Quiz).filter(Quiz.name == name).offset(skip).limit(limit).all()

    def get_multi_by_participant(
        self, db: Session, *, student: models.User, skip: int = 0, limit: int = 100
    ) -> List[Quiz]:
        """Read quizzes answered by the student."""

        quizzes = []
        unique_attempts = crud.quiz_attempt.get_multi_latest_by_student_id(
            db, student_id=student.id
        )
        for attempt in unique_attempts:
            quiz_in_db = crud.quiz.get(db, id=attempt.quiz_id)

            quiz = jsonable_encoder(quiz_in_db)
            quiz["questions"] = quiz_in_db.questions
            quiz["answers"] = jsonable_encoder(
                crud.quiz_answer.get_all_by_attempt(db, attempt_id=attempt.id)
            )
            quiz["score"] = crud.quiz_attempt.get_score(db, id=attempt.id)
            quiz["participant_name"] = crud.user.get(
                db, id=attempt.student_id
            ).full_name

            quizzes.append(quiz)

        return quizzes

    def get_multi_results_by_quiz_id(
        self, db: Session, *, id: int, skip: int = 0, limit: int = 100
    ) -> List[models.QuizReadWithQuestions]:
        """Read results for the quiz"""

        quizzes = []
        unique_attempts = crud.quiz_attempt.get_multi_latest_by_quiz_id(db, id=id)
        for attempt in unique_attempts:
            quiz_in_db = crud.quiz.get(db, id=id)
            quiz = jsonable_encoder(quiz_in_db)
            quiz["questions"] = quiz_in_db.questions
            quiz["answers"] = jsonable_encoder(
                crud.quiz_answer.get_all_by_attempt(db, attempt_id=attempt.id)
            )
            quiz["score"] = crud.quiz_attempt.get_score(db, id=attempt.id)
            quiz["participant_name"] = crud.user.get(
                db, id=attempt.student_id
            ).full_name
            quizzes.append(quiz)

        return quizzes

    def get_multi_by_author(
        self, db: Session, *, teacher_id: int, skip: int = 0, limit: int = 100
    ) -> List[Quiz]:
        """Read quizzes participated by the student."""
        return (
            db.query(Quiz)
            .filter(Quiz.teacher_id == teacher_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def has_question(self, db: Session, quiz_index: Union[int, str], question_id: int):
        """Verify if question belongs to the quiz"""
        quiz = self.get_by_index(db, quiz_index)
        question_ids = [question.id for question in quiz.questions]
        return question_id in question_ids

    def is_author(self, db: Session, user_id: int, quiz_index: Union[int, str]):
        quiz = self.get_by_index(db, quiz_index)
        return quiz.teacher_id == user_id


quiz = CRUDQuiz(Quiz)
