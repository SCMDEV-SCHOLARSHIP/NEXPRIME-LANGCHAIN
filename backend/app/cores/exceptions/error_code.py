from pydantic import BaseModel


class ErrorCode(BaseModel):
    code: str
    message: str
