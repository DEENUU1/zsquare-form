from sqlalchemy.orm import Session
from models.client import Client
from fastapi import HTTPException


def client_exists_by_email(db: Session, email: str):
    return db.query(Client).filter(Client.email == email).first() is not None


def client_exists_by_id(db: Session, client_id: int):
    return db.query(Client).filter(Client.id == client_id).first() is not None


def get_client_by_email_phone(db: Session, email: str, phone: str):
    return db.query(Client).filter(Client.email == email, Client.phone == phone).first()


def create_client(db: Session, client: Client):
    existing_client = get_client_by_email_phone(db, client.email, client.phone)
    if existing_client:
        return existing_client

    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def get_clients(db: Session):
    return db.query(Client).all()


def delete_client_by_id(db: Session, client_id: int):
    if not client_exists_by_id(db, client_id):
        raise HTTPException(status_code=404, detail="Client not found")

    db.query(Client).filter(Client.id == client_id).delete()
    db.commit()


def get_client_by_id(db: Session, client_id: int):
    if not client_exists_by_id(db, client_id):
        raise HTTPException(status_code=404, detail="Client not found")

    return db.query(Client).filter(Client.id == client_id).first()


def search_clients(db: Session, query: str):
    return db.query(Client).filter(Client.full_name.ilike(f"%{query}%")).all()
