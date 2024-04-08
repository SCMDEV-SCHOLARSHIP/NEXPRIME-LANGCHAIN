from sqlalchemy import String, TIMESTAMP, BOOLEAN
from sqlalchemy.sql.schema import Column
from datetime import datetime

from app.database.rdb.session import Base


class JWTToken(Base):
    __tablename__ = "nsa_refresh_token"

    user_id = Column("user_id", String, primary_key=True)
    refresh_token = Column("refresh_token", String, nullable=False)
    create_datetime = Column(TIMESTAMP, nullable=False, default=datetime.now)
    create_user_id = Column(String, nullable=False, default=user_id)
    modified_datetime = Column(TIMESTAMP, nullable=False, default=datetime.now)
    modified_user_id = Column(String, nullable=False, default=user_id)
    delete_yn = Column(BOOLEAN, default=False)
