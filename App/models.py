from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from .database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)

    movie_statuses = relationship(
        "UserMovieStatus", back_populates="user", cascade="all, delete-orphan"
    )

    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    watch_schedules = relationship(
        "WatchSchedule", back_populates="user", cascade="all, delete-orphan"
    )


class Movie(Base):
    """Catalog of movies shared across all users.

    Movies come from external sources (TMDB, etc.) and are not owned by any user.
    Per-user state (watched, rating) lives in UserMovieStatus.
    """

    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(String(200), nullable=False)
    genre = Column(String(50), nullable=False, index=True)
    external_rating = Column(Numeric(3, 1), nullable=True)
    external_id = Column(String(50), nullable=True)
    external_source = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    statuses = relationship(
        "UserMovieStatus", back_populates="movie", cascade="all, delete-orphan"
    )
    schedules = relationship(
        "WatchSchedule", back_populates="movie", cascade="all, delete-orphan"
    )
    __table_args__ = (
        UniqueConstraint("external_source", "external_id", name="uq_movie_external"),
    )


class UserMovieStatus(Base):
    """Per-user state for a catalog movie.

    A row exists only when the user has interacted with the movie
    (marked as watched or assigned a rating). Missing row = untouched.
    """

    __tablename__ = "user_movie_status"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    movie_id = Column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    watched = Column(Boolean, nullable=False, default=False)
    rating = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("Users", back_populates="movie_statuses")
    movie = relationship("Movie", back_populates="statuses")

    __table_args__ = (UniqueConstraint("user_id", "movie_id", name="uq_user_movie"),)


class Notification(Base):
    """In-app notification for a user.

    Created by background tasks (e.g. welcome on signup).
    Read flag lets the frontend show an unread badge.
    """

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    message = Column(String(500), nullable=False)
    read = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("Users", back_populates="notifications")


class WatchSchedule(Base):
    """User-planned movie to watch on a specific date.

    status: pending (default) -> done (user marked watched)
                              -> missed (date passed without done)
    Celery Beat checks daily and sends notifications for today's schedules.
    """

    __tablename__ = "watch_schedules"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    movie_id = Column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scheduled_date = Column(Date, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending", index=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("Users", back_populates="watch_schedules")
    movie = relationship("Movie", back_populates="schedules")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "movie_id",
            "scheduled_date",
            name="uq_user_movie_date",
        ),
    )
