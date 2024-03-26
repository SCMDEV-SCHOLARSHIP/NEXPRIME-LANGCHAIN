from sqlalchemy import String
from sqlalchemy.sql.schema import Column
from app.database.rdb.session import Base


class JWTToken(Base):
    __tablename__ = "nsa_refresh_token"

    user_id = Column("user_id", String, primary_key=True)
    refresh_token = Column("refresh_token", String, nullable=False)
