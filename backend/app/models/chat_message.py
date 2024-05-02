from sqlalchemy import String, TIMESTAMP, BOOLEAN, ARRAY, Integer, UUID
from sqlalchemy.sql.schema import Column
from datetime import datetime

from app.cores.utils import same_as
from app.database.rdb.session import Base


class MessageHistory(Base):
    __tablename__ = "nsa_message_history"

    message_id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    sender = Column(String, nullable=False)
    content = Column(String, nullable=False)
    sources = Column(ARRAY(String), nullable=True)
    create_datetime = Column(TIMESTAMP, nullable=False, default=datetime.now)
    create_user_id = Column(String, nullable=False, default=same_as("user_id"))
    modified_datetime = Column(TIMESTAMP, nullable=False, default=datetime.now)
    modified_user_id = Column(String, nullable=False, default=same_as("user_id"))
    delete_yn = Column(BOOLEAN, default=False)
