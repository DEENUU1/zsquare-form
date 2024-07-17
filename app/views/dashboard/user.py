from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette import status

from config.database import get_db
from models.user import User
from services.auth import verify_password, get_user_by_email, create_access_token, get_password_hash
from config.settings import settings

router = APIRouter(
    prefix="/user",
    tags=["Users"],
)


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return settings.TEMPLATES.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = get_user_by_email(db, email)

    if not user.is_active:
        return settings.TEMPLATES.TemplateResponse(
            "login.html",
            {"request": request, "error": "Użytkownik jest nieaktywny"}
        )

    if not user or not verify_password(password, user.hashed_password):
        return settings.TEMPLATES.TemplateResponse(
            "login.html",
            {"request": request, "error": "Nieprawidłowe dane logowania"}
        )
    access_token = create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/dashboard/clients", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/user/login", status_code=303)
    response.delete_cookie(key="access_token")
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return settings.TEMPLATES.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register(
        request: Request,
        full_name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = get_user_by_email(db, email)
    if user:
        return settings.TEMPLATES.TemplateResponse(
            "register.html",
            {"request": request, "error": "Użytkownik już istnieje"}
        )

    hashed_password = get_password_hash(password)
    new_user = User(email=email, full_name=full_name, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/user/login", status_code=status.HTTP_302_FOUND)
