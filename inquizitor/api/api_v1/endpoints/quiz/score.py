
from sqlmodel import Session
from typing import Any, List, Union

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi_jwt_auth import AuthJWT

from inquizitor import crud, models
from inquizitor.api import deps

router = APIRouter()

@router.get("/{index}/scores")
async def read_quiz_scores(
	*,
	db: Session = Depends(deps.get_db),
	index: Union[int, str] = Path(..., description="ID or Code of quiz to retrieve"),
	current_user: models.User = Depends(deps.get_current_user)
) -> Any:
	"""
	Retrieve quiz participants scores by quiz id or quiz_code.
	"""

	# check permissions
	if not crud.user.is_superuser(current_user) and \
		not crud.quiz.is_author(db, user_id=current_user.id, quiz_index=id):
		raise HTTPException(status_code=400, detail="Not enough permissions")

	quiz = crud.quiz.get(db, id=index) # NOTE can be made a dependency function for ease of reuse

	if not quiz:
		raise HTTPException(status_code=404, detail="Quiz not found")

	participants = quiz.students
	quiz_scores = []

	for participant in participants:
		quiz_scores.append(
			{
				"id": participant.id,
				"username": participant.username,
				"score": crud.quiz_attempt.get_score(db, quiz_id=quiz.id, student_id=participant.id)
			}
			)

	return quiz_scores