import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db.session import get_db
from app.models.exercise import Exercise
from app.routes.admin import require_admin
from app.services.exercise_import import ImportStats, SeedStats, apply_curated_seed_file, import_exercise_file

router = APIRouter(tags=["exercises"])


class ExerciseRead(BaseModel):
    id: uuid.UUID
    source_id: str
    name: str
    ru_name: str | None = None
    body_part: str | None = None
    target: str | None = None
    secondary_muscles: list[str]
    equipment: str | None = None
    movement_pattern: str | None = None
    difficulty: str | None = None
    image_path: str | None = None
    gif_path: str | None = None
    image_url: str | None = None
    gif_url: str | None = None
    instructions: dict[str, object] | list[object] | None = None
    instruction_steps: list[str] | None = None
    curation_status: str
    avoid_reason: str | None = None

    model_config = {"from_attributes": True}


class ImportResponse(BaseModel):
    created: int
    updated: int

    @classmethod
    def from_stats(cls, stats: ImportStats) -> "ImportResponse":
        return cls(created=stats.created, updated=stats.updated)


class SeedResponse(BaseModel):
    seeded: int
    missing: int

    @classmethod
    def from_stats(cls, stats: SeedStats) -> "SeedResponse":
        return cls(seeded=stats.seeded, missing=stats.missing)


@router.get("/exercises", response_model=list[ExerciseRead])
def list_exercises(
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[Exercise]:
    statement = select(Exercise).order_by(Exercise.name).offset(offset).limit(limit)
    return list(db.scalars(statement).all())


@router.get("/exercises/search", response_model=list[ExerciseRead])
def search_exercises(
    db: Annotated[Session, Depends(get_db)],
    q: str = Query(min_length=1),
    equipment: str | None = None,
    body_part: str | None = None,
    movement_pattern: str | None = None,
    curation_status: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[Exercise]:
    statement = select(Exercise).where(Exercise.name.ilike(f"%{q}%")).order_by(Exercise.name).limit(limit)
    if equipment:
        statement = statement.where(Exercise.equipment == equipment)
    if body_part:
        statement = statement.where(Exercise.body_part == body_part)
    if movement_pattern:
        statement = statement.where(Exercise.movement_pattern == movement_pattern)
    if curation_status:
        statement = statement.where(Exercise.curation_status == curation_status)
    return list(db.scalars(statement).all())


@router.get("/exercises/{exercise_id}", response_model=ExerciseRead)
def get_exercise(exercise_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]) -> Exercise:
    exercise = db.scalars(select(Exercise).where(Exercise.id == exercise_id)).one_or_none()
    if exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    return exercise


@router.post(
    "/admin/exercises/import",
    response_model=ImportResponse,
    dependencies=[Depends(require_admin)],
)
def admin_import_exercises(
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ImportResponse:
    stats = import_exercise_file(db, Path(settings.exercises_dataset_path))
    return ImportResponse.from_stats(stats)


@router.post(
    "/admin/exercises/seed-curated",
    response_model=SeedResponse,
    dependencies=[Depends(require_admin)],
)
def admin_seed_curated(
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> SeedResponse:
    stats = apply_curated_seed_file(db, Path(settings.curated_exercises_seed_path))
    return SeedResponse.from_stats(stats)
