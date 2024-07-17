import base64
import os
import tempfile

from fastapi import APIRouter, Request, Depends, Form, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from config.database import get_db
from models.client import Client
from services.auth import get_current_user
from config.settings import settings
from services.client_service import create_client, get_clients, get_client_by_id, delete_client_by_id
from services.form_data_service import get_forms_by_client_id, delete_form_by_id
from services.report_service import get_report_by_form_id
from utils.model_serializer import serialize_model

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/clients", response_class=HTMLResponse)
def get_clients_handler(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/user/login")

    clients = get_clients(db)
    return settings.TEMPLATES.TemplateResponse(
        "clients.html",
        {
            "request": request,
            "clients": clients,
            "user": current_user
        }
    )


@router.get("/clients/{client_id}", response_class=HTMLResponse)
def get_client_handler(request: Request, client_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/user/login")

    client = get_client_by_id(db, client_id)
    forms_raw = get_forms_by_client_id(db, client_id)
    forms = [serialize_model(form) for form in forms_raw]

    return settings.TEMPLATES.TemplateResponse(
        "client.html",
        {
            "request": request,
            "client": client,
            "forms": forms,
            "user": current_user
        }
    )


@router.post("/clients", response_class=RedirectResponse)
def create_client_handler(
        request: Request,
        full_name: str = Form(...),
        email: str = Form(...),
        phone: str = Form(...),
        db: Session = Depends(get_db)
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/user/login")

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
        return RedirectResponse("/user/login")

    delete_client_by_id(db, client_id)
    return {"message": "Client deleted successfully"}


@router.delete("/forms/{form_id}")
def delete_form_handler(request: Request, form_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/user/login")

    delete_form_by_id(db, form_id)
    return {"message": "Form deleted successfully"}


@router.get("/forms/{form_id}/report")
def get_report_handler(request: Request, form_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/user/login")

    report = get_report_by_form_id(db, form_id)
    if not report or not report.report_content:
        raise HTTPException(status_code=404, detail="Report not found")

    report_content = base64.b64decode(report.report_content)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(report_content)
        temp_file_path = temp_file.name

    return FileResponse(
        path=temp_file_path,
        filename="report.pdf",
        media_type="application/pdf",
        background=BackgroundTask(lambda: os.unlink(temp_file_path))
    )
