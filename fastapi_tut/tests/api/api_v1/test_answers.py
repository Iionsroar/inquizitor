# TODO
# remove unused imports by ctrl+D-ing
import logging
import pytest
from httpx import AsyncClient
from sqlmodel import Session
from typing import Dict

from fastapi.encoders import jsonable_encoder

from fastapi_tut import crud
from fastapi_tut.tests.factories import AnswerFactory, QuizFactory

@pytest.mark.anyio
class TestReadQuizzes:
	async def test_update_answer_superuser(
		self, db: Session, client: AsyncClient, superuser_cookies: Dict[str, str]
	) -> None:
		superuser_cookies = await superuser_cookies
		r = await client.get(
			"/users/profile", cookies=superuser_cookies
		)
		result = r.json()
		user = crud.user.get(db, id=result['id'])

		quiz = crud.quiz.get(db, id=1)
		question = crud.quiz_question.get(db, id=1)
		choice = crud.quiz_choice.get(db, id=1)
		answer_in = AnswerFactory.stub(schema_type="create", student=user, choice=choice)

		r = await client.put(
			f"/quizzes/{quiz.id}/questions/{question.id}/answer", cookies=superuser_cookies, json=answer_in
		)
		assert r.status_code == 400

	async def test_update_answer_teacher(
		self, db: Session, client: AsyncClient, teacher_cookies: Dict[str, str]
	) -> None:
		teacher_cookies = await teacher_cookies
		r = await client.get(
			"/users/profile", cookies=teacher_cookies
		)
		result = r.json()
		user = crud.user.get(db, id=result['id'])

		quiz = crud.quiz.get(db, id=1)
		question = crud.quiz_question.get(db, id=1)
		choice = crud.quiz_choice.get(db, id=1)
		answer_in = AnswerFactory.stub(schema_type="create", student=user, choice=choice)

		r = await client.put(
			f"/quizzes/{quiz.id}/questions/{question.id}/answer", cookies=teacher_cookies, json=answer_in
		)
		assert r.status_code == 400

	async def test_update_answer_student(
		self, db: Session, client: AsyncClient, student_cookies: Dict[str, str]
	) -> None:
		student_cookies = await student_cookies
		r = await client.get(
			"/users/profile", cookies=student_cookies
		)
		result = r.json()
		user = crud.user.get(db, id=result['id'])

		quiz = crud.quiz.get(db, id=1)
		question = crud.quiz_question.get(db, id=1)
		choice = crud.quiz_choice.get(db, id=1)
		answer_in = AnswerFactory.stub(schema_type="create", student=user, choice=choice)

		r = await client.put(
			f"/quizzes/{quiz.id}/questions/{question.id}/answer", 
			cookies=student_cookies, 
			json=answer_in
		)
		result = r.json()
		assert r.status_code == 200
		assert result["content"] == answer_in["content"]
		assert result["is_correct"] == answer_in["is_correct"]
		assert result["student_id"] == answer_in["student_id"]
		assert result["choice_id"] == answer_in["choice_id"]