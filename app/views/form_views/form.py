import requests
from fastapi import Depends, Request, Form, BackgroundTasks, APIRouter
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse
from config.settings import settings

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


def submit_form_to_api(form_data):
    url = settings.API_URL + "submit-form"
    response = requests.post(url, data=form_data)
    return response.json()


@router.post("/submit-form")
def submit_form(
        request: Request,
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
):
    try:
        form_data = {
            "full_name": full_name,
            "birth_date": birth_date,
            "location": location,
            "phone": phone,
            "email": email,
            "bike_brand": bike_brand,
            "bike_model": bike_model,
            "bike_size": bike_size,
            "bike_year": bike_year,
            "drive_group": drive_group,
            "year_distance": year_distance,
            "weekly_frequency": weekly_frequency,
            "avg_kilometer": avg_kilometer,
            "ride_style": ride_style,
            "event": event,
            "other_activity": other_activity,
            "visit_goal": visit_goal,
            "visit_problems": visit_problems,
            "injuries": injuries,
        }

        response = submit_form_to_api(form_data)
        return response

    except Exception as e:
        return {"error": "Wystąpił błąd, spróbuj ponownie później."}


@router.get("/thank-you", response_class=HTMLResponse)
def thank_you(request: Request):
    context = {"request": request}
    return settings.TEMPLATES.TemplateResponse("thank_you.html", context)
