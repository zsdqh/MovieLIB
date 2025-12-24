from fastapi import APIRouter

from backend.src.auth.auth.presentation.api import jwt_api_router
from backend.src.auth.confirmations.presentation.api import conf_api_router
from backend.src.auth.users.presentation.users_api import user_api_router

v1_routers = APIRouter(prefix="/v1")
v1_routers.include_router(user_api_router)
v1_routers.include_router(jwt_api_router)
v1_routers.include_router(conf_api_router)
