from app.database.db_config import get_db
from app.models.user import User


def get_user_list() -> list[User]:
    db = next(get_db())
    user_list = db.query(User).all()
    return user_list


def create_user(user: User) -> User:
    db = next(get_db())
    user.create_user_id = user.user_id
    user.modified_user_id = user.user_id
    db.add(user)
    db.commit()
    ret_user = db.query(User).filter_by(user_id=user.user_id).first()
    return ret_user


def delete_user(user_id: str) -> User:
    db = next(get_db())
    record_to_delete = db.query(User).filter(User.user_id == user_id).first()
    deleted = record_to_delete
    db.delete(record_to_delete)
    db.commit()
    return deleted
