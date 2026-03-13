from fastapi import APIRouter

from . import installations, zones, devices

api_router = APIRouter()

api_router.include_router(
    installations.router,
    prefix="/installations",
    tags=["Installations"]
)
api_router.include_router(
    zones.router,
    prefix="/zones",
    tags=["Zones"]
)
api_router.include_router(
    devices.router,
    prefix="/devices",
    tags=["Devices"]
)
