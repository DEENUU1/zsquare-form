from fastapi import APIRouter
from views.form_views import form
from views.dashboard import user, dashboard

router = APIRouter(
    prefix=""
)

router.include_router(form.router)
router.include_router(user.router)
router.include_router(dashboard.router)
