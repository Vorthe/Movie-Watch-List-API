from database import Base
from sqlalchemy import Column, Integer, String, Boolean


class Movies(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    rating = Column(Integer)
    watched = Column(Boolean, default=False)






class Users(Base):
    __tablename__='users'
    username=Column(String,unique=True)
    email=Column(String,unique=True)
    first_name=Column(String)
    last_name=Column(String)
    password=Column(String)
    verify_password=Column(String)
    name=Column(String)
    name=Column(String)