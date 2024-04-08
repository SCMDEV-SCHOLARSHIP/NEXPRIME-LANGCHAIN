from pydantic import BaseModel


class LoginRequest(BaseModel, extra="forbid"):
    user_id: str
    user_password: str
    login_type: str = "form_base"


class LoginDTO(BaseModel, extra="forbid"):
    user_id: str
    user_password: str
