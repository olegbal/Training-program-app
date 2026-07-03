import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.workout import WorkoutExercise


class WorkoutSet(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "sets"

    workout_exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workout_exercises.id"),
        nullable=False,
    )
    set_index: Mapped[int] = mapped_column(Integer, nullable=False)
    weight: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    reps: Mapped[int | None] = mapped_column(Integer)
    rpe: Mapped[Decimal | None] = mapped_column(Numeric(3, 1))
    is_warmup: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    notes: Mapped[str | None] = mapped_column(Text)

    workout_exercise: Mapped["WorkoutExercise"] = relationship(back_populates="sets")
