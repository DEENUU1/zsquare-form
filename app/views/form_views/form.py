from fastapi import Depends, Request, Form, BackgroundTasks, APIRouter
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse

from config.database import get_db
from config.settings import settings
from models.client import Client
from models.form_data import FormData
from services.client_service import client_exists_by_email
from tasks.save_form import save_form_data

router = APIRouter(
    prefix="",
    tags=["Form"],
)


@router.get("/", response_class=HTMLResponse)
def home(
        request: Request,
):
    context = {"request": request}
    return settings.TEMPLATES.TemplateResponse("form.html", context)


@router.post("/submit-form")
def submit_form(
        request: Request,
        background_tasks: BackgroundTasks,
        full_name: str = Form(...),
        birth_date: str = Form(None),
        location: str = Form(None),
        phone: str = Form(...),
        email: str = Form(...),
        bike_brand: str = Form(None),
        bike_model: str = Form(None),
        bike_size: str = Form(None),
        bike_year: str = Form(None),
        drive_group: str = Form(None),
        year_distance: str = Form(None),
        weekly_frequency: str = Form(None),
        avg_kilometer: str = Form(None),
        ride_style: str = Form(None),
        event: str = Form(None),
        other_activity: str = Form(None),
        visit_goal: str = Form(...),
        visit_problems: str = Form(None),
        injuries: str = Form(None),
        db: Session = Depends(get_db),
):
    try:
        existing_user = client_exists_by_email(db, email)
        if not existing_user:
            return {"error": "Podaj poprawny adres email."}

        client = Client(full_name=full_name, birth_date=birth_date, location=location, phone=phone, email=email)

        form_data = FormData(
            bike_brand=bike_brand,
            bike_model=bike_model,
            bike_size=bike_size,
            bike_year=bike_year,
            drive_group=drive_group,
            year_distance=year_distance,
            weekly_frequency=weekly_frequency,
            avg_kilometer=avg_kilometer,
            ride_style=ride_style,
            event=event,
            other_activity=other_activity,
            visit_goal=visit_goal,
            visit_problems=visit_problems,
            injuries=injuries,
        )

        background_tasks.add_task(save_form_data, db, client, form_data)
        return {"message": "Formularz wysłany!"}
    except Exception as e:
        return {"error": "Wystąpił błąd, spróbuj ponownie później."}


@router.get("/thank-you", response_class=HTMLResponse)
def thank_you(request: Request):
    context = {"request": request}
    return settings.TEMPLATES.TemplateResponse("thank_you.html", context)
