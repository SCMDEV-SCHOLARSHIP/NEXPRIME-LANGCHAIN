from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.cores.config import settings


SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{settings.environ.db_username}:{settings.environ.db_password}@{settings.environ.db_url}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    echo_pool="debug",
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
    finally:
        db.close()
