from sqlalchemy import String
from sqlalchemy.sql.schema import Column
from app.database.rdb.session import Base


class JWTToken(Base):
    __tablename__ = "token"

    user_id = Column("UserID", String, primary_key=True, nullable=False)
    refresh_token = Column("RefreshToken", String, nullable=False)
