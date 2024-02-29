""" 
TODO: Test를 위한 파일로 DB 사용되는 API 만들어진 후 삭제 
실제 사용시 Service부터 dao까지 작성 필요...
각 Layer를 어떻게 구현해야할지 고민 필요...
"""
from fastapi import APIRouter, status
from app.models.user import User
from app.schemas.test_schema import UserDTO
from app.database.db_config import get_db

router = APIRouter(prefix="/test")


@router.get(
    "/",
    response_model=list[UserDTO],
    status_code=status.HTTP_200_OK,
)
def get_users() -> UserDTO:
    db = next(get_db())

    users = db.query(User).all()
    response = []
    for user in users:
        response.append(UserDTO(user_id=user.user_id, user_name=user.user_name))
    return response

@router.post(
    "/",
    response_model=UserDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_user(user:UserDTO) -> UserDTO:
    db = next(get_db())
    
    db.add(User(user_id=user.user_id, user_name=user.user_name, create_user_id=user.user_id, modified_user_id=user.user_id))
    db.commit()
    return user