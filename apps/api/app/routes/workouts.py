import uuid
from datetime import date
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.exercise import Exercise
from app.models.set import WorkoutSet
from app.models.template import TemplateExercise, WorkoutTemplate
from app.models.user import User
from app.models.workout import WorkoutExercise, WorkoutSession
from app.routes.admin import require_admin
from app.services.workout_sessions import (
    WorkoutExerciseNotFoundError,
    WorkoutSessionNotFoundError,
    WorkoutTemplateNotFoundError,
    add_workout_set,
    complete_workout_exercise,
    complete_workout_session,
    start_today_session,
)
from app.services.workout_templates import SeedTemplatesStats, project_weekday, seed_workout_templates

router = APIRouter(tags=["workouts"])


class WorkoutTemplateSeedResponse(BaseModel):
    templates_seeded: int
    exercises_seeded: int

    @classmethod
    def from_stats(cls, stats: SeedTemplatesStats) -> "WorkoutTemplateSeedResponse":
        return cls(templates_seeded=stats.templates_seeded, exercises_seeded=stats.exercises_seeded)


class TodaySessionRead(BaseModel):
    id: uuid.UUID | None
    date: date
    title: str
    day_type: str
    focus: str
    status: str


class TodayExerciseRead(BaseModel):
    id: uuid.UUID | None
    slot_name: str
    status: str
    planned_sets: str
    planned_reps: str | None
    planned_rpe: str | None
    rest: str | None
    exercise: dict[str, object | None] | None
    sets: list[object]


class TodayWorkoutRead(BaseModel):
    session: TodaySessionRead
    exercises: list[TodayExerciseRead]


class WorkoutSetCreate(BaseModel):
    weight: Decimal | None = None
    reps: int | None = None
    rpe: Decimal | None = None
    is_warmup: bool = False
    notes: str | None = None


class WorkoutSetRead(BaseModel):
    id: uuid.UUID
    set_index: int
    weight: Decimal | None = None
    reps: int | None = None
    rpe: Decimal | None = None
    is_warmup: bool
    notes: str | None = None


@router.post(
    "/admin/workouts/seed-templates",
    response_model=WorkoutTemplateSeedResponse,
    dependencies=[Depends(require_admin)],
)
def admin_seed_workout_templates(db: Annotated[Session, Depends(get_db)]) -> WorkoutTemplateSeedResponse:
    return WorkoutTemplateSeedResponse.from_stats(seed_workout_templates(db))


@router.get("/workouts/today", response_model=TodayWorkoutRead)
def get_today_workout(
    db: Annotated[Session, Depends(get_db)],
    requested_date: Annotated[date | None, Query(alias="date")] = None,
) -> TodayWorkoutRead:
    requested_date = requested_date or date.today()
    template = db.scalars(
        select(WorkoutTemplate).where(WorkoutTemplate.weekday == project_weekday(requested_date))
    ).one_or_none()
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout template is not seeded")

    return TodayWorkoutRead(
        session=TodaySessionRead(
            id=None,
            date=requested_date,
            title=template.title,
            day_type=template.code,
            focus=template.focus,
            status="planned",
        ),
        exercises=[_serialize_template_exercise(item) for item in template.template_exercises],
    )


@router.post("/workouts/today/start", response_model=TodayWorkoutRead)
def start_today_workout(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    requested_date: Annotated[date | None, Query(alias="date")] = None,
) -> TodayWorkoutRead:
    try:
        session = start_today_session(db, user=current_user, requested_date=requested_date or date.today())
    except WorkoutTemplateNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout template is not seeded") from None
    return _serialize_workout_session(session)


@router.post("/workouts/{session_id}/complete", response_model=TodayWorkoutRead)
def complete_workout(
    session_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TodayWorkoutRead:
    try:
        session = complete_workout_session(db, user=current_user, session_id=session_id)
    except WorkoutSessionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout session was not found") from None
    return _serialize_workout_session(session)


@router.post("/workout-exercises/{workout_exercise_id}/sets", response_model=WorkoutSetRead)
def create_workout_set(
    workout_exercise_id: uuid.UUID,
    payload: WorkoutSetCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> WorkoutSetRead:
    try:
        workout_set = add_workout_set(
            db,
            user=current_user,
            workout_exercise_id=workout_exercise_id,
            weight=payload.weight,
            reps=payload.reps,
            rpe=payload.rpe,
            is_warmup=payload.is_warmup,
            notes=payload.notes,
        )
    except WorkoutExerciseNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout exercise was not found") from None
    return _serialize_workout_set(workout_set)


@router.post("/workout-exercises/{workout_exercise_id}/complete", response_model=TodayExerciseRead)
def complete_exercise(
    workout_exercise_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TodayExerciseRead:
    try:
        workout_exercise = complete_workout_exercise(db, user=current_user, workout_exercise_id=workout_exercise_id)
    except WorkoutExerciseNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout exercise was not found") from None
    return _serialize_workout_exercise(workout_exercise)


def _serialize_template_exercise(item: TemplateExercise) -> TodayExerciseRead:
    return TodayExerciseRead(
        id=item.id,
        slot_name=item.slot_name,
        status="planned",
        planned_sets=_range_text(item.planned_sets_min, item.planned_sets_max),
        planned_reps=item.reps_text or _optional_range_text(item.reps_min, item.reps_max),
        planned_rpe=_rpe_text(item.rpe_min, item.rpe_max),
        rest=_rest_text(item.rest_seconds_min, item.rest_seconds_max),
        exercise=_serialize_exercise(item.exercise),
        sets=[],
    )


def _serialize_workout_session(session: WorkoutSession) -> TodayWorkoutRead:
    focus = session.template.focus if session.template is not None else ""
    return TodayWorkoutRead(
        session=TodaySessionRead(
            id=session.id,
            date=session.date,
            title=session.title,
            day_type=session.day_type,
            focus=focus,
            status=session.status,
        ),
        exercises=[_serialize_workout_exercise(item) for item in session.workout_exercises],
    )


def _serialize_workout_exercise(item: WorkoutExercise) -> TodayExerciseRead:
    return TodayExerciseRead(
        id=item.id,
        slot_name=item.slot_name,
        status=item.status,
        planned_sets=_range_text(item.planned_sets_min, item.planned_sets_max),
        planned_reps=item.reps_text,
        planned_rpe=item.rpe_text,
        rest=item.rest_text,
        exercise=_serialize_exercise(item.exercise),
        sets=[_serialize_workout_set(workout_set) for workout_set in item.sets],
    )


def _serialize_workout_set(workout_set: WorkoutSet) -> WorkoutSetRead:
    return WorkoutSetRead(
        id=workout_set.id,
        set_index=workout_set.set_index,
        weight=workout_set.weight,
        reps=workout_set.reps,
        rpe=workout_set.rpe,
        is_warmup=workout_set.is_warmup,
        notes=workout_set.notes,
    )


def _serialize_exercise(exercise: Exercise | None) -> dict[str, object | None] | None:
    if exercise is None:
        return None
    return {
        "id": str(exercise.id),
        "name": exercise.name,
        "ru_name": exercise.ru_name,
        "equipment": exercise.equipment,
        "target": exercise.target,
        "image_url": exercise.image_url,
        "gif_url": exercise.gif_url,
    }


def _range_text(min_value: int, max_value: int) -> str:
    if min_value == max_value:
        return str(min_value)
    return f"{min_value}-{max_value}"


def _optional_range_text(min_value: int | None, max_value: int | None) -> str | None:
    if min_value is None or max_value is None:
        return None
    return _range_text(min_value, max_value)


def _rpe_text(min_value: Decimal | None, max_value: Decimal | None) -> str | None:
    if min_value is None and max_value is None:
        return None
    if min_value is None:
        return _format_decimal(max_value)
    if max_value is None or min_value == max_value:
        return _format_decimal(min_value)
    return f"{_format_decimal(min_value)}-{_format_decimal(max_value)}"


def _rest_text(min_seconds: int | None, max_seconds: int | None) -> str | None:
    if min_seconds is None and max_seconds is None:
        return None
    if min_seconds is None:
        return _seconds_text(max_seconds)
    if max_seconds is None or min_seconds == max_seconds:
        return _seconds_text(min_seconds)
    if min_seconds % 60 == 0 and max_seconds % 60 == 0:
        return f"{min_seconds // 60}-{max_seconds // 60} min"
    return f"{min_seconds}-{max_seconds} sec"


def _seconds_text(value: int | None) -> str | None:
    if value is None:
        return None
    if value % 60 == 0:
        return f"{value // 60} min"
    return f"{value} sec"


def _format_decimal(value: Decimal | None) -> str | None:
    if value is None:
        return None
    if value == value.to_integral_value():
        return str(value.to_integral_value())
    return f"{value:g}"
