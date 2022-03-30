import datetime as dt
import logging
import pytest
from httpx import AsyncClient
from pprint import pformat
from sqlmodel import Session
from typing import Dict

from fastapi.encoders import jsonable_encoder

from fastapi_tut import crud
from fastapi_tut.tests.factories import QuestionFactory, QuizFactory

logging.basicConfig(level=logging.INFO)

DT_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

@pytest.mark.anyio
class TestReadQuestion:
	async def test_read_question_student(
		self, client: AsyncClient, student_cookies: Dict[str, str]
	) -> None:
		question = QuestionFactory()
		r = await client.get(
			f"/quizzes/{question.quiz_id}/questions/{question.id}", cookies=await student_cookies
		)
		result = r.json()
		assert r.status_code == 200
		assert result["content"] == question.content
		assert result["points"] == question.points
		assert result["order"] == question.order
		assert result["quiz_id"] == question.quiz_id

	async def test_read_question_teacher(
		self, client: AsyncClient, teacher_cookies: Dict[str, str]
	) -> None:
		question = QuestionFactory()
		r = await client.get(
			f"/quizzes/{question.quiz_id}/questions/{question.id}", cookies=await teacher_cookies
		)
		result = r.json()
		assert r.status_code == 200
		assert result["content"] == question.content
		assert result["points"] == question.points
		assert result["order"] == question.order
		assert result["quiz_id"] == question.quiz_id

	async def test_read_question_superuser(
		self, client: AsyncClient, superuser_cookies: Dict[str, str]
	) -> None:
		question = QuestionFactory()
		r = await client.get(
			f"/quizzes/{question.quiz_id}/questions/{question.id}", cookies=await superuser_cookies
		)
		result = r.json()
		assert r.status_code == 200
		assert result["content"] == question.content
		assert result["points"] == question.points
		assert result["order"] == question.order
		assert result["quiz_id"] == question.quiz_id

@pytest.mark.anyio
class TestUpdateQuestion:
	async def test_update_question_student(
		self, client: AsyncClient, student_cookies: Dict[str, str]
	) -> None:
		question = QuestionFactory()
		question_in = QuestionFactory.stub(schema_type="update", quiz_id=3)
		r = await client.put(
			f"/quizzes/{question.quiz_id}/questions/{question.id}", 
			cookies=await student_cookies,
			json=question_in
		)
		result = r.json()
		assert r.status_code == 400

	async def test_update_question_teacher_not_author(
		self, client: AsyncClient, teacher_cookies: Dict[str, str]
	) -> None:
		question = QuestionFactory()
		question_in = QuestionFactory.stub(schema_type="update", quiz_id=3)
		r = await client.put(
			f"/quizzes/{question.quiz_id}/questions/{question.id}", 
			cookies=await teacher_cookies,
			json=question_in
		)
		result = r.json()
		assert r.status_code == 400

	async def test_update_question_teacher_is_author(
		self, db: Session, client: AsyncClient, teacher_cookies: Dict[str, str]
	) -> None:
		teacher_cookies = await teacher_cookies
		# TODO replace with get-user when implemented
		r = await client.post(
			"/login/test-token", cookies=teacher_cookies
		)
		result = r.json()
		# logging.info(f"{result}")
		teacher = crud.user.get(db, id=result['id'])
		quiz = QuizFactory(teacher=teacher)
		repr(quiz) 

		question = QuestionFactory(quiz=quiz)
		question_in = QuestionFactory.stub(schema_type="update")
		r = await client.put(
			f"/quizzes/{question.quiz_id}/questions/{question.id}", 
			cookies=teacher_cookies,
			json=question_in
		)
		result = r.json()
		assert r.status_code == 200
		assert result["content"] == question_in["content"]
		assert result["points"] == question_in["points"]
		assert result["order"] == question_in["order"]

	async def test_update_question_teacher_is_author(
		self, client: AsyncClient, superuser_cookies: Dict[str, str]
	) -> None:
		question = QuestionFactory()
		question_in = QuestionFactory.stub(schema_type="update")
		r = await client.put(
			f"/quizzes/{question.quiz_id}/questions/{question.id}", 
			cookies=await superuser_cookies,
			json=question_in
		)
		result = r.json()
		assert r.status_code == 200
		assert result["content"] == question_in["content"]
		assert result["points"] == question_in["points"]
		assert result["order"] == question_in["order"]