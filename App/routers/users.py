from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from models import Movies, Users
from database import SessionLocal
from starlette import status
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(prefix="/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]
bycrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dep, db: db_dep):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user: user_dep, db: db_dep, user_verification: UserVerification
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentiction Failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bycrypt_context.verify(
        user_verification.password, user_model.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Error On Password Change")
    user_model.hashed_password = bycrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
