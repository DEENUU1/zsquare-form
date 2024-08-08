from fastapi import APIRouter
from views.form_views import form

router = APIRouter(
    prefix=""
)

router.include_router(form.router)
