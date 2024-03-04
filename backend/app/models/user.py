# TODO: Test를 위한 파일로 DB 사용되는 API 만들어진 후 삭제
from sqlalchemy import String, TIMESTAMP
from sqlalchemy.sql.schema import Column
from app.database.db_config import Base
from datetime import datetime


class User(Base):
    __tablename__ = "t_scm_user_m"

    user_id = Column(String, primary_key=True)
    user_name = Column(String, nullable=False)
    create_datetime = Column(TIMESTAMP, nullable=False, default=datetime.now)
    create_user_id = Column(String, nullable=False, default=user_id)
    modified_datetime = Column(TIMESTAMP, nullable=False, default=datetime.now)
    modified_user_id = Column(String, nullable=False, default=user_id)
