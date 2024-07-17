from sqlalchemy.orm import Session

from models.client import Client
from models.form_data import FormData
from services.client_service import create_client
from services.form_data_service import create_form_data


def save_form_data(db: Session, client: Client, form_data: FormData) -> None:
    client_obj = create_client(db, client)
    create_form_data(db, form_data, client_obj.id)
    return
