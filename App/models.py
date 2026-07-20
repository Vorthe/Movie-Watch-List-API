from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Integer, default=True)
    role = Column(String)


class Movies(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    rating = Column(Integer)
    watched = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
