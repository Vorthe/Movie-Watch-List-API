from database import Base
from sqlalchemy import Column, Integer, String, Boolean


class Movies(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    rating = Column(Integer)
    watched = Column(Boolean, default=False)
