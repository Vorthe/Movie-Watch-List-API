from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Path
from pydantic import BaseModel, Field
from ..models import Users
from ..tasks import send_welcome_notification
from ..database import SessionLocal
from sqlalchemy.orm import Session
import bcrypt
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

# from fastapi.templating import Jinja2Templates

load_dotenv()


router = APIRouter(prefix="/auth", tags=["auth"])


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUserRequest(BaseModel):
    email: str
    full_name: str
    password: str = Field(min_length=6)


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dep = Annotated[Session, Depends(get_db)]
# templates = Jinja2Templates(directory="App/templates")

### Pages ###


# @router.get("/login-page")
# def render_login_page(request: Request):
#     return templates.TemplateResponse(
#         request=request, name="login.html", context={"request": request}
#     )


# @router.get("/register-page")
# def render_register_page(request: Request):
#     return templates.TemplateResponse(
#         request=request, name="register.html", context={"request": request}
#     )


### Endpoints ###
def authentication_user(username: str, password: str, db):
    # Accept either username or email
    user = (
        db.query(Users)
        .filter((Users.username == username) | (Users.email == username))
        .first()
    )
    if not user:
        return False
    password_bytes = password.encode("utf-8")[:72]
    hashed_password_bytes = user.hashed_password.encode("utf-8")
    if not bcrypt.checkpw(password_bytes, hashed_password_bytes):
        return False
    return user


def create_access_token(
    username: str, user_id: int, role: str, expires_delta: timedelta
):

    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could Not Validate User.",
            )
        return {"username": username, "id": user_id, "user_role": user_role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could Not Validate User."
        )


user_dep = Annotated[dict, Depends(get_current_user)]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dep, create_user_request: CreateUserRequest):
    # Split full_name into first and last
    parts = create_user_request.full_name.strip().split(maxsplit=1)
    first_name = parts[0] if parts else ""
    last_name = parts[1] if len(parts) > 1 else ""

    password_bytes = create_user_request.password.encode("utf-8")[:72]
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.email,  # email as username
        first_name=first_name,
        last_name=last_name,
        hashed_password=hashed_password,
        role="user",
        is_active=True,
        phone_number=None,
    )
    db.add(create_user_model)
    db.commit()

    send_welcome_notification.delay(create_user_model.id)


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dep
):
    user = authentication_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed Authentication",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        user.username, user.id, user.role, timedelta(minutes=20)
    )

    return {"access_token": token, "token_type": "bearer"}


class RoleUpdateRequest(BaseModel):
    role: str = Field(pattern="^(user|admin)$")


@router.put("/users/{user_id}/role", status_code=200)
async def update_user_role(
    db: db_dep,
    user: user_dep,
    payload: RoleUpdateRequest,
    user_id: int = Path(gt=0),
):
    """Promote or demote a user. Admin-only."""
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    target = db.query(Users).filter(Users.id == user_id).first()
    if target is None:
        raise HTTPException(status_code=404, detail="User Not Found")

    target.role = payload.role
    db.commit()
    return {"id": target.id, "username": target.username, "role": target.role}
