import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.exercise import Exercise
    from app.models.set import WorkoutSet
    from app.models.template import WorkoutTemplate
    from app.models.user import User


class WorkoutSession(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workout_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    template_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("workout_templates.id"))
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    day_type: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="planned", server_default="planned")
    energy: Mapped[str | None] = mapped_column(Text)
    sleep: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="workout_sessions")
    template: Mapped["WorkoutTemplate | None"] = relationship(back_populates="workout_sessions")
    workout_exercises: Mapped[list["WorkoutExercise"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="WorkoutExercise.order_index",
    )


class WorkoutExercise(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workout_exercises"

    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workout_sessions.id"), nullable=False)
    exercise_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("exercises.id"))
    replaced_from_exercise_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("exercises.id"))
    slot_name: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_sets_min: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_sets_max: Mapped[int] = mapped_column(Integer, nullable=False)
    reps_text: Mapped[str | None] = mapped_column(Text)
    rpe_text: Mapped[str | None] = mapped_column(Text)
    rest_text: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="planned", server_default="planned")
    notes: Mapped[str | None] = mapped_column(Text)

    session: Mapped[WorkoutSession] = relationship(back_populates="workout_exercises")
    exercise: Mapped["Exercise | None"] = relationship(
        back_populates="workout_exercises",
        foreign_keys=[exercise_id],
    )
    replaced_from_exercise: Mapped["Exercise | None"] = relationship(foreign_keys=[replaced_from_exercise_id])
    sets: Mapped[list["WorkoutSet"]] = relationship(
        back_populates="workout_exercise",
        cascade="all, delete-orphan",
        order_by="WorkoutSet.set_index",
    )
