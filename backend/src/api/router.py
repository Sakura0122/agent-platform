from fastapi import APIRouter

from api.auth.router import router as auth_router
from api.captcha.router import router as captcha_router
from api.permission.router import router as permission_router
from api.role.router import router as role_router
from api.user.router import router as user_router

api_router = APIRouter(prefix="/api")
api_router.include_router(captcha_router)
api_router.include_router(user_router)
api_router.include_router(auth_router)
api_router.include_router(role_router)
api_router.include_router(permission_router)
