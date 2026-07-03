import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.exercise import Exercise
    from app.models.workout import WorkoutSession


class WorkoutTemplate(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workout_templates"

    code: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    focus: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    template_exercises: Mapped[list["TemplateExercise"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="TemplateExercise.order_index",
    )
    workout_sessions: Mapped[list["WorkoutSession"]] = relationship(back_populates="template")


class TemplateExercise(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "template_exercises"

    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workout_templates.id"),
        nullable=False,
    )
    exercise_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("exercises.id"))
    slot_name: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_sets_min: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_sets_max: Mapped[int] = mapped_column(Integer, nullable=False)
    reps_min: Mapped[int | None] = mapped_column(Integer)
    reps_max: Mapped[int | None] = mapped_column(Integer)
    reps_text: Mapped[str | None] = mapped_column(Text)
    rpe_min: Mapped[Decimal | None] = mapped_column(Numeric(3, 1))
    rpe_max: Mapped[Decimal | None] = mapped_column(Numeric(3, 1))
    rest_seconds_min: Mapped[int | None] = mapped_column(Integer)
    rest_seconds_max: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)

    template: Mapped[WorkoutTemplate] = relationship(back_populates="template_exercises")
    exercise: Mapped["Exercise | None"] = relationship(back_populates="template_exercises")
