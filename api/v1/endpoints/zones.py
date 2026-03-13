from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared import schemas
from shared.database import get_db
from shared.models import Zone as ZoneModel

router = APIRouter()


@router.post("/", response_model=schemas.Zone)
async def create_zone(zone: schemas.ZoneCreate, db: AsyncSession = Depends(get_db)):
    db_zone = ZoneModel(**zone.model_dump())
    db.add(db_zone)
    await db.commit()
    await db.refresh(db_zone)
    return db_zone


@router.get("/", response_model=list[schemas.Zone])
async def get_zones(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ZoneModel))
    return result.scalars().all()
