import logging
from typing import Generic, Any, Dict, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from sqlmodel import Session
from pydantic import BaseModel

from fastapi_tut.db.base_class import TableBase

logging.basicConfig(level=logging.INFO)

ModelType = TypeVar("ModelType", bound=TableBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
	def __init__(self, model: Type[ModelType]):
		"""
		CRUD object with default methods to Create, Read, Update, Delete (CRUD).

		**Parameters**

		* `model`: A SQLAlchemy model class
		* `schema`: A Pydantic model (schema) class
		"""
		self.model = model

	def get(self, db: Session, id: Any) -> Optional[ModelType]:
		return db.query(self.model).filter(self.model.id == id).first()

	def get_multi(
		self, db: Session, *, skip: int = 0, limit: int = 100
	) -> List[ModelType]:
		return db.query(self.model).offset(skip).limit(limit).all()

	def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
		obj_in_data = jsonable_encoder(obj_in)
		db_obj = self.model(**obj_in_data)  # type: ignore
		db.add(db_obj)
		db.commit()
		db.refresh(db_obj)
		return db_obj

	def update(
		self,
		db: Session,
		*,
		db_obj: ModelType,
		obj_in: Union[UpdateSchemaType, Dict[str, Any]]
	) -> ModelType:
		obj_data = jsonable_encoder(db_obj)
		if isinstance(obj_in, dict):
			update_data = obj_in
		else:
			update_data = obj_in.dict(exclude_unset=True)
		# NOTE (awaiting creator updates): exclude_unset does not work in SQLModels but does work in Pydantic Models
		update_data = {k: v for k, v in update_data.items() if v is not None}
		for field in obj_data:
			if field in update_data: 
				setattr(db_obj, field, update_data[field])
		db.add(db_obj)
		db.commit()
		db.refresh(db_obj)
		return db_obj

	def remove(self, db: Session, *, id: int) -> ModelType:
		obj = db.query(self.model).get(id)
		db.delete(obj)
		db.commit()
		return obj