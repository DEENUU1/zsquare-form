from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.user import User


def get_users(db: Session):
    return db.query(User).all()


def user_exists_by_id(db: Session, client_id: int):
    return db.query(User).filter(User.id == client_id).first() is not None


def delete_user_by_id(db: Session, client_id: int):
    if not user_exists_by_id(db, client_id):
        raise HTTPException(status_code=404, detail="User not found")

    db.query(User).filter(User.id == client_id).delete()
    db.commit()


def update_is_active_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = 1 if user.is_active == 0 else 0
    db.commit()
    db.refresh(user)
    return user.is_active
