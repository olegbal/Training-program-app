from typing import TYPE_CHECKING

from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.template import TemplateExercise
    from app.models.workout import WorkoutExercise


class Exercise(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "exercises"

    source_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    ru_name: Mapped[str | None] = mapped_column(Text)
    body_part: Mapped[str | None] = mapped_column(Text)
    target: Mapped[str | None] = mapped_column(Text)
    secondary_muscles: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    equipment: Mapped[str | None] = mapped_column(Text)
    movement_pattern: Mapped[str | None] = mapped_column(Text, index=True)
    difficulty: Mapped[str | None] = mapped_column(Text)
    image_path: Mapped[str | None] = mapped_column(Text)
    gif_path: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text)
    gif_url: Mapped[str | None] = mapped_column(Text)
    instructions: Mapped[dict[str, object] | list[object] | None] = mapped_column(JSONB)
    instruction_steps: Mapped[list[str] | None] = mapped_column(JSONB)
    curation_status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="unreviewed",
        server_default="unreviewed",
    )
    avoid_reason: Mapped[str | None] = mapped_column(Text)

    template_exercises: Mapped[list["TemplateExercise"]] = relationship(back_populates="exercise")
    workout_exercises: Mapped[list["WorkoutExercise"]] = relationship(
        back_populates="exercise",
        foreign_keys="WorkoutExercise.exercise_id",
    )
