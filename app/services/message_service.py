from sqlalchemy.orm import Session
from schemas.message_schema import MessageOutputSchema, MessageInputSchema
from typing import List
from models.message import Message


def create_message(
        db: Session,
        message: MessageInputSchema
) -> MessageOutputSchema:
    message = Message(**message.dict())
    db.add(message)
    db.commit()
    db.refresh(message)

    return MessageOutputSchema.from_orm(message)


def get_messages_by_form_id(
        db: Session,
        form_id: int
) -> List[MessageOutputSchema]:
    messages = db.query(Message).filter(Message.form_id == form_id).all()

    return [MessageOutputSchema.from_orm(message) for message in messages]
