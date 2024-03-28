from sqlalchemy import String, TIMESTAMP, BOOLEAN
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.schema import Column
from app.database.rdb.session import Base
from datetime import datetime

class File(Base):
    __tablename__ = "nsa_embedding_file"

    uuid = Column(UUID(as_uuid=True), primary_key=True)
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_extension = Column(String, nullable=False)
    create_datetime = Column(TIMESTAMP, nullable=False, default=datetime.now)
    create_user_id = Column(String, nullable=False, default="")
    modified_datetime = Column(TIMESTAMP, nullable=False, default=datetime.now)
    modified_user_id = Column(String, nullable=False, default="")
    delete_yn = Column(BOOLEAN, default=False)
