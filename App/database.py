from dotenv import load_dotenv
import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import OperationalError

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def create_engine_with_retry(url, retries=5, delay=3):
    for attempt in range(retries):
        try:

            engine = create_engine(
                url,
                pool_pre_ping=True,
                poolclass=NullPool,
                connect_args={"sslmode": "require"},  # برای External URL الزامی است
            )

            with engine.connect() as conn:
                pass
            return engine
        except OperationalError as e:
            if attempt == retries - 1:
                raise
            print(
                f"Database connection failed (attempt {attempt + 1}/{retries}), retrying in {delay}s..."
            )
            time.sleep(delay)


engine = create_engine_with_retry(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
