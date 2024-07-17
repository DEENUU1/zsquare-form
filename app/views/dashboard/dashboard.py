from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from config.database import get_db
from models.client import Client
from services.auth import get_current_user
from config.settings import settings
from services.client_service import create_client, get_clients, get_client_by_id, delete_client_by_id
from services.form_data_service import get_forms_by_client_id, delete_form_by_id


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/clients", response_class=HTMLResponse)
def get_clients_handler(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/")

    clients = get_clients(db)
    return settings.TEMPLATES.TemplateResponse("clients.html", {"request": request, "clients": clients})


@router.get("/clients/{client_id}", response_class=HTMLResponse)
def get_client_handler(request: Request, client_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/")

    client = get_client_by_id(db, client_id)
    forms = get_forms_by_client_id(db, client_id)
    return settings.TEMPLATES.TemplateResponse(
        "client.html",
        {
            "request": request,
            "client": client,
            "forms": forms
        }
    )


@router.post("/clients",  response_class=RedirectResponse)
def create_client_handler(
        request: Request,
        full_name: str = Form(...),
        email: str = Form(...),
        phone: str = Form(...),
        db: Session = Depends(get_db)
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/")

    client = create_client(db, Client(
        full_name=full_name,
        email=email,
        phone=phone,
    ))
    return RedirectResponse(url=f"/dashboard/clients/{client.id}", status_code=303)


@router.delete("/clients/{client_id}")
def delete_client_handler(request: Request, client_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/")

    delete_client_by_id(db, client_id)
    return {"message": "Client deleted successfully"}


@router.delete("/forms/{form_id}")
def delete_form_handler(request: Request, form_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/")

    delete_form_by_id(db, form_id)
    return {"message": "Form deleted successfully"}
