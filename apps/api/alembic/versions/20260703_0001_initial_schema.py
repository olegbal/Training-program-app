"""initial schema

Revision ID: 20260703_0001
Revises:
Create Date: 2026-07-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260703_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "exercises",
        sa.Column("source_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("ru_name", sa.Text(), nullable=True),
        sa.Column("body_part", sa.Text(), nullable=True),
        sa.Column("target", sa.Text(), nullable=True),
        sa.Column("secondary_muscles", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("equipment", sa.Text(), nullable=True),
        sa.Column("movement_pattern", sa.Text(), nullable=True),
        sa.Column("difficulty", sa.Text(), nullable=True),
        sa.Column("image_path", sa.Text(), nullable=True),
        sa.Column("gif_path", sa.Text(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("gif_url", sa.Text(), nullable=True),
        sa.Column("instructions", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("instruction_steps", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("curation_status", sa.Text(), server_default="unreviewed", nullable=False),
        sa.Column("avoid_reason", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_exercises_movement_pattern"), "exercises", ["movement_pattern"], unique=False)
    op.create_index(op.f("ix_exercises_name"), "exercises", ["name"], unique=False)
    op.create_index(op.f("ix_exercises_source_id"), "exercises", ["source_id"], unique=True)

    op.create_table(
        "users",
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.Text(), nullable=True),
        sa.Column("first_name", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_telegram_id"), "users", ["telegram_id"], unique=True)

    op.create_table(
        "workout_templates",
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("focus", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workout_templates_code"), "workout_templates", ["code"], unique=True)
    op.create_index(op.f("ix_workout_templates_weekday"), "workout_templates", ["weekday"], unique=False)

    op.create_table(
        "template_exercises",
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exercise_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("slot_name", sa.Text(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("planned_sets_min", sa.Integer(), nullable=False),
        sa.Column("planned_sets_max", sa.Integer(), nullable=False),
        sa.Column("reps_min", sa.Integer(), nullable=True),
        sa.Column("reps_max", sa.Integer(), nullable=True),
        sa.Column("reps_text", sa.Text(), nullable=True),
        sa.Column("rpe_min", sa.Numeric(3, 1), nullable=True),
        sa.Column("rpe_max", sa.Numeric(3, 1), nullable=True),
        sa.Column("rest_seconds_min", sa.Integer(), nullable=True),
        sa.Column("rest_seconds_max", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"]),
        sa.ForeignKeyConstraint(["template_id"], ["workout_templates.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "workout_sessions",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("day_type", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), server_default="planned", nullable=False),
        sa.Column("energy", sa.Text(), nullable=True),
        sa.Column("sleep", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["template_id"], ["workout_templates.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workout_sessions_date"), "workout_sessions", ["date"], unique=False)

    op.create_table(
        "workout_exercises",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exercise_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("replaced_from_exercise_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("slot_name", sa.Text(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("planned_sets_min", sa.Integer(), nullable=False),
        sa.Column("planned_sets_max", sa.Integer(), nullable=False),
        sa.Column("reps_text", sa.Text(), nullable=True),
        sa.Column("rpe_text", sa.Text(), nullable=True),
        sa.Column("rest_text", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), server_default="planned", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"]),
        sa.ForeignKeyConstraint(["replaced_from_exercise_id"], ["exercises.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["workout_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "sets",
        sa.Column("workout_exercise_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("set_index", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Numeric(7, 2), nullable=True),
        sa.Column("reps", sa.Integer(), nullable=True),
        sa.Column("rpe", sa.Numeric(3, 1), nullable=True),
        sa.Column("is_warmup", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workout_exercise_id"], ["workout_exercises.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("sets")
    op.drop_table("workout_exercises")
    op.drop_index(op.f("ix_workout_sessions_date"), table_name="workout_sessions")
    op.drop_table("workout_sessions")
    op.drop_table("template_exercises")
    op.drop_index(op.f("ix_workout_templates_weekday"), table_name="workout_templates")
    op.drop_index(op.f("ix_workout_templates_code"), table_name="workout_templates")
    op.drop_table("workout_templates")
    op.drop_index(op.f("ix_users_telegram_id"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_exercises_source_id"), table_name="exercises")
    op.drop_index(op.f("ix_exercises_name"), table_name="exercises")
    op.drop_index(op.f("ix_exercises_movement_pattern"), table_name="exercises")
    op.drop_table("exercises")
