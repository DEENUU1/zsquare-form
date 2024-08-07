from sqlalchemy.orm import Session

from models.client import Client
from models.form_data import FormData
from schemas.message_schema import MessageInputSchema
from services.client_service import create_client
from services.form_data_service import create_form_data
from services.message_service import create_message


def save_form_data(db: Session, client: Client, form_data: FormData) -> None:
    client_obj = create_client(db, client)
    created_form = create_form_data(db, form_data, client_obj.id)

    # Create welcome message in chat
    create_message(db, MessageInputSchema(
        role="assistant",
        text="Proszę podać wzrost klienta",
        form_id=created_form.id,
    ))

    return
