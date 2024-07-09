from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from sqlalchemy import ForeignKey, Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from sqlalchemy.orm import relationship
import os


load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")  #  "sqlite:///database.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # connect_args={"check_same_thread": False},
)
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
    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)


class Client(Base):
    __tablename__ = "client"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String, nullable=False)
    birth_date = Column(String, nullable=True)
    location = Column(String, nullable=True)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    form = relationship("FormData", backref="client", cascade="all, delete-orphan")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    Client.metadata.create_all(bind=engine)
    FormData.metadata.create_all(bind=engine)


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


@app.get("/", response_class=HTMLResponse)
def home(
        request: Request,
):
    context = {"request": request}
    return templates.TemplateResponse("base.html", context)


@app.post("/submit-form")
def submit_form(
        request: Request,
        full_name: str = Form(...),
        birth_date: str = Form(None),
        location: str = Form(None),
        phone: str = Form(...),
        email: str = Form(...),
        bike: str = Form(None),
        shoes: str = Form(None),
        inserts: str = Form(None),
        pedals: str = Form(None),
        otherBike: str = Form(None),
        adnotation: str = Form(None),
        sportHistory: str = Form(None),
        sportHistoryAdnotation: str = Form(None),
        db: Session = Depends(get_db)
):
    client = Client(
        full_name=full_name,
        birth_date=birth_date,
        location=location,
        phone=phone,
        email=email
    )

    form_data = FormData(
        bike=bike,
        boots=shoes,
        insoles=inserts,
        pedals=pedals,
        other_bikes=otherBike,
        tool_annotation=adnotation,
        sport_history=sportHistory,
        sport_annotation=sportHistoryAdnotation
    )

    client = create_client(db, client)
    create_form_data(db, form_data, client.id)

    return {"message": "Form submitted successfully"}
