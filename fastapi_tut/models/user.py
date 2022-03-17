from email.policy import default
from enum import unique
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, String

from fastapi_tut.db.base_class import TableBase
from fastapi_tut.models import MarksOfUser

# Shared Properties
class UserBase(SQLModel):
	full_name: Optional[str] = Field(index=True)
	email: Optional[EmailStr]
	is_superuser: bool = Field(default=False)


# Properties to receive via API on creation
class UserCreate(UserBase):
	email: EmailStr
	password: str


class UserUpdate(UserBase):
	full_name: Optional[str] = None
	email: Optional[EmailStr] = None
	is_superuser: bool = False
	password: Optional[str] = None


class UserInDBBase(UserBase, TableBase):
	class Config:
		orm_mode = True


# Additional properties  to return via API
class User(UserInDBBase, table=True):
	id : Optional[int] = Field(default=None, primary_key=True)
	username : str = Field(sa_column=Column(unique=True, nullable=False))
	email: EmailStr = Field(sa_column=Column(String, unique=True, nullable=False))
	password: str = Field(nullable=False)
	last_name : str = Field(nullable=False)
	first_name : str = Field(nullable=False)
	is_student : bool = Field(nullable=False)
	is_teacher : bool = Field(nullable=False)

	marks: Optional[MarksOfUser] = Relationship(back_populates="user")

	def __repr__(self):
		"""Represent instance as a unique string."""
		return f"<User({self.email!r})>"
