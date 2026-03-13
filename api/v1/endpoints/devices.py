from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared import schemas
from shared.database import get_db
from shared.models import Device as DeviceModel
from shared.utils import generate_unique_slug

router = APIRouter()


@router.post("/", response_model=schemas.Device)
async def create_device(device: schemas.DeviceCreate, db: AsyncSession = Depends(get_db)):
    db_device = DeviceModel(**device.model_dump())
    db_device.topic = generate_unique_slug(device.name)
    db.add(db_device)
    await db.commit()
    await db.refresh(db_device)
    return db_device


@router.get("/", response_model=list[schemas.Device])
async def get_devices(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeviceModel))
    return result.scalars().all()
