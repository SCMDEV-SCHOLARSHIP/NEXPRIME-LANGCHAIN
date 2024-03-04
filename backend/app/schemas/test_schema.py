# TODO: Test를 위한 파일로 DB 사용되는 API 만들어진 후 삭제
from pydantic import BaseModel


class UserDTO(BaseModel, extra="forbid"):
    user_id: str
    user_name: str