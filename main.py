from fastapi import FastAPI, Request, Form, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os
from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, func, create_engine, Boolean
from sqlalchemy.orm import relationship
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum
from clickup import validate_user
import logging


logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")


app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

engine = create_engine(SQLALCHEMY_DATABASE_URL,)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class FormData(Base):
    __tablename__ = "form"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bike = Column(String, nullable=True)
    boots = Column(String, nullable=True)
    insoles = Column(String, nullable=True)
    pedals = Column(String, nullable=True)
    other_bikes = Column(String, nullable=True)
    tool_annotation = Column(String, nullable=True)
    sport_history = Column(String, nullable=True)
    sport_annotation = Column(String, nullable=True)
    position_problem = Column(String, nullable=True)
    adnotation_position_problem = Column(String, nullable=True)
    years_cycling = Column(Integer, nullable=True)
    annual_mileage = Column(Integer, nullable=True)
    weekly_rides = Column(Integer, nullable=True)
    session_duration = Column(String, nullable=True)
    participated_in_races = Column(Boolean, nullable=True)
    best_results = Column(String, nullable=True)
    intensity_measurement = Column(String, nullable=True)
    other_sports = Column(String, nullable=True)
    bike_confidence = Column(Integer, nullable=True)
    gear_changing = Column(Boolean, nullable=True)
    autumn_winter_riding = Column(Boolean, nullable=True)
    preferred_grip = Column(String, nullable=True)
    cadence_comfort = Column(String, nullable=True)
    group_riding_skills = Column(String, nullable=True)
    cornering_style = Column(String, nullable=True)
    brake_usage = Column(String, nullable=True)
    tire_pressure_check = Column(String, nullable=True)
    injuries = Column(String, nullable=True)
    injuries_during_cycling = Column(Boolean, nullable=True)
    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)
    message = relationship("Message", backref="form", cascade="all, delete-orphan")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Client(Base):
    __tablename__ = "client"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String, nullable=False)
    birth_date = Column(String, nullable=True)
    location = Column(String, nullable=True)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    form = relationship("FormData", backref="client", cascade="all, delete-orphan")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Role(Enum):
    assistant = "assistant"
    user = "user"
    system = "system"


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(SQLAlchemyEnum(Role), nullable=False)
    text = Column(String, nullable=False)
    form_id = Column(Integer, ForeignKey("form.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    Client.metadata.create_all(bind=engine)
    FormData.metadata.create_all(bind=engine)
    Message.metadata.create_all(bind=engine)


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


def create_form_data(db: Session, form_data: FormData, client_id: int):
    form_data.client_id = client_id
    db.add(form_data)
    db.commit()
    db.refresh(form_data)
    return form_data


def save_to_database(db: Session, client: Client, form_data: FormData) -> None:
    client_obj = create_client(db, client)
    create_form_data(db, form_data, client_obj.id)
    return


@app.get("/", response_class=HTMLResponse)
def home(
        request: Request,
):
    context = {"request": request}
    return templates.TemplateResponse("base.html", context)


@app.post("/submit-form")
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
        validated_user, user_id = validate_user(email)

        if not validated_user:
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

        background_tasks.add_task(save_to_database, db, client, form_data)
        return {"message": "Formularz wysłany!"}
    except Exception as e:
        logger.error(e)
        return {"error": "Wystąpił błąd, spróbuj ponownie później."}

