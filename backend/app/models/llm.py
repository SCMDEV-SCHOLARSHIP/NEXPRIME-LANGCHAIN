from sqlalchemy import String, TIMESTAMP, DOUBLE, INTEGER, BOOLEAN
from sqlalchemy.sql.schema import Column
from app.database.rdb.session import Base
from datetime import datetime

class Llm(Base):
    __tablename__ = "nsa_llm_model"
    
    llm_id = Column(INTEGER, primary_key=True, autoincrement=True)
    llm_type = Column(String, nullable=False)
    llm_name = Column(String, nullable=False)
    inference_server_url = Column(String)
    max_new_tokens = Column(INTEGER)
    top_k = Column(INTEGER)
    top_p = Column(DOUBLE)
    typical_p = Column(DOUBLE)
    temperature = Column(DOUBLE)
    repetition_penalty = Column(DOUBLE)
    streaming = Column(BOOLEAN)
    api_key = Column(String)
    create_datetime = Column(TIMESTAMP, nullable=False, default=datetime.now)
    create_user_id = Column(String, nullable=False, default="")
    modified_datetime = Column(TIMESTAMP, nullable=False, default=datetime.now)
    modified_user_id = Column(String, nullable=False, default="")
    delete_yn = Column(BOOLEAN, default=False)