from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared import schemas
# Importamos lo que construimos en el monorepo
from shared.database import get_db
from shared.models import Installation as InstallationModel
from shared.utils import generate_unique_slug

router = APIRouter()


# Endpoint para crear una instalación
@router.post("/installations/", response_model=schemas.Installation)
async def create_installation(
        installation: schemas.InstallationCreate,
        db: AsyncSession = Depends(get_db)
):
    generated_topic_prefix = generate_unique_slug(installation.name)

    # Creamos el objeto de base de datos
    db_installation = InstallationModel(
        name=installation.name,
        topic_prefix=generated_topic_prefix,
        description=installation.description
    )

    db.add(db_installation)
    await db.commit()
    await db.refresh(db_installation)
    return db_installation


# Endpoint para listar todas las instalaciones
@router.get("/installations/", response_model=list[schemas.Installation])
async def get_installations(db: AsyncSession = Depends(get_db)):
    query = select(InstallationModel)
    result = await db.execute(query)
    return result.scalars().all()
