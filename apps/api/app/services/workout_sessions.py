import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.template import TemplateExercise, WorkoutTemplate
from app.models.user import User
from app.models.workout import WorkoutExercise, WorkoutSession
from app.services.workout_templates import project_weekday


class WorkoutTemplateNotFoundError(LookupError):
    pass


class WorkoutSessionNotFoundError(LookupError):
    pass


def start_today_session(db: Session, *, user: User, requested_date: date) -> WorkoutSession:
    existing_session = db.scalars(
        select(WorkoutSession).where(WorkoutSession.user_id == user.id, WorkoutSession.date == requested_date)
    ).one_or_none()
    if existing_session is not None:
        if existing_session.status == "planned":
            existing_session.status = "started"
            existing_session.started_at = existing_session.started_at or datetime.now(UTC)
            db.commit()
            db.refresh(existing_session)
        return existing_session

    template = db.scalars(
        select(WorkoutTemplate).where(WorkoutTemplate.weekday == project_weekday(requested_date))
    ).one_or_none()
    if template is None:
        raise WorkoutTemplateNotFoundError

    session = WorkoutSession(
        user_id=user.id,
        template_id=template.id,
        template=template,
        date=requested_date,
        title=template.title,
        day_type=template.code,
        status="started",
        started_at=datetime.now(UTC),
    )
    session.workout_exercises = [_copy_template_exercise(item) for item in template.template_exercises]
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def complete_workout_session(db: Session, *, user: User, session_id: uuid.UUID) -> WorkoutSession:
    session = db.scalars(
        select(WorkoutSession).where(WorkoutSession.id == session_id, WorkoutSession.user_id == user.id)
    ).one_or_none()
    if session is None:
        raise WorkoutSessionNotFoundError

    now = datetime.now(UTC)
    session.status = "completed"
    session.started_at = session.started_at or now
    session.completed_at = now
    db.commit()
    db.refresh(session)
    return session


def _copy_template_exercise(item: TemplateExercise) -> WorkoutExercise:
    return WorkoutExercise(
        exercise_id=item.exercise_id,
        exercise=item.exercise,
        slot_name=item.slot_name,
        order_index=item.order_index,
        planned_sets_min=item.planned_sets_min,
        planned_sets_max=item.planned_sets_max,
        reps_text=item.reps_text or _optional_range_text(item.reps_min, item.reps_max),
        rpe_text=_rpe_text(item.rpe_min, item.rpe_max),
        rest_text=_rest_text(item.rest_seconds_min, item.rest_seconds_max),
        status="planned",
    )


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
