from sqlalchemy import String, TIMESTAMP
from sqlalchemy.sql.schema import Column
from app.database.rdb.session import Base
from datetime import datetime


class User(Base):
    __tablename__ = "nsa_user"

    user_id = Column(String, primary_key=True)
    user_name = Column(String, nullable=True)
    user_email = Column(String, nullable=False)
    user_password = Column(String, nullable=False)
    create_datetime = Column(TIMESTAMP, nullable=False, default=datetime.now)
    create_user_id = Column(String, nullable=False, default=user_id)
    modified_datetime = Column(TIMESTAMP, nullable=False, default=datetime.now)
    modified_user_id = Column(String, nullable=False, default=user_id)
