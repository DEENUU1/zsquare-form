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
        bike: str = Form(None),
        shoes: str = Form(None),
        inserts: str = Form(None),
        pedals: str = Form(None),
        other_bike: str = Form(None),
        adnotation: str = Form(None),
        sport_history: str = Form(None),
        sport_history_adnotation: str = Form(None),
        position_problem: str = Form(None),
        adnotation_position_problem: str = Form(None),
        years_cycling: int = Form(None),
        annual_mileage: int = Form(None),
        weekly_rides: int = Form(None),
        session_duration: str = Form(None),
        participated_in_races: bool = Form(None),
        best_results: str = Form(None),
        intensity_measurement: str = Form(None),
        other_sports: str = Form(None),
        bike_confidence: int = Form(None),
        gear_changing: bool = Form(None),
        autumn_winter_riding: bool = Form(None),
        preferred_grip: str = Form(None),
        cadence_comfort: str = Form(None),
        group_riding_skills: str = Form(None),
        cornering_style: str = Form(None),
        brake_usage: str = Form(None),
        tire_pressure_check: str = Form(None),
        injuries: str = Form(None),
        injuries_during_cycling: bool = Form(None),
        db: Session = Depends(get_db),
):
    try:

        existing_user = client_exists_by_email(db, email)

        if not existing_user:
            return {"error": "Podaj poprawny adres email."}

        client = Client(full_name=full_name, birth_date=birth_date, location=location, phone=phone, email=email)

        form_data = FormData(
            bike=bike,
            boots=shoes,
            insoles=inserts,
            pedals=pedals,
            other_bikes=other_bike,
            tool_annotation=adnotation,
            sport_history=sport_history,
            sport_annotation=sport_history_adnotation,
            position_problem=position_problem,
            adnotation_position_problem=adnotation_position_problem,
            years_cycling=years_cycling,
            annual_mileage=annual_mileage,
            weekly_rides=weekly_rides,
            session_duration=session_duration,
            participated_in_races=participated_in_races,
            best_results=best_results,
            intensity_measurement=intensity_measurement,
            other_sports=other_sports,
            bike_confidence=bike_confidence,
            gear_changing=gear_changing,
            autumn_winter_riding=autumn_winter_riding,
            preferred_grip=preferred_grip,
            cadence_comfort=cadence_comfort,
            group_riding_skills=group_riding_skills,
            cornering_style=cornering_style,
            brake_usage=brake_usage,
            tire_pressure_check=tire_pressure_check,
            injuries=injuries,
            injuries_during_cycling=injuries_during_cycling
        )

        background_tasks.add_task(save_form_data, db, client, form_data)
        return {"message": "Formularz wysłany!"}
    except Exception as e:
        return {"error": "Wystąpił błąd, spróbuj ponownie później."}


@router.get("/thank-you", response_class=HTMLResponse)
def thank_you(request: Request):
    context = {"request": request}
    return settings.TEMPLATES.TemplateResponse("thank_you.html", context)
