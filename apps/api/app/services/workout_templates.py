from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.models.template import TemplateExercise, WorkoutTemplate


@dataclass(frozen=True)
class TemplateSlotSeed:
    slot_name: str
    exercise_names: tuple[str, ...]
    planned_sets_min: int
    planned_sets_max: int
    reps_min: int | None = None
    reps_max: int | None = None
    reps_text: str | None = None
    rpe_min: Decimal | None = None
    rpe_max: Decimal | None = None
    rest_seconds_min: int | None = None
    rest_seconds_max: int | None = None
    notes: str | None = None


@dataclass(frozen=True)
class WorkoutTemplateSeed:
    code: str
    title: str
    weekday: int
    focus: str
    description: str | None
    slots: tuple[TemplateSlotSeed, ...]


@dataclass(frozen=True)
class SeedTemplatesStats:
    templates_seeded: int = 0
    exercises_seeded: int = 0


def rpe(value: str) -> Decimal:
    return Decimal(value)


DEFAULT_TEMPLATE_SEEDS: tuple[WorkoutTemplateSeed, ...] = (
    WorkoutTemplateSeed(
        code="rest_sunday",
        title="Восстановление",
        weekday=0,
        focus="восстановление / прогулка / мобильность",
        description="Rest day.",
        slots=(),
    ),
    WorkoutTemplateSeed(
        code="legs_a",
        title="Ноги A",
        weekday=1,
        focus="квадрицепсы + ягодицы + икры",
        description="Hard but controlled quad-focused lower-body session.",
        slots=(
            TemplateSlotSeed(
                "Жим ногами / hack squat / squat",
                ("sled 45 degrees leg press", "lever leg press"),
                4,
                4,
                6,
                10,
                "6-10",
                rpe("7.5"),
                rpe("9.0"),
                120,
                180,
            ),
            TemplateSlotSeed(
                "Болгарский сплит-присед",
                ("dumbbell bulgarian split squat",),
                3,
                3,
                8,
                12,
                "8-12 each leg",
                rpe("8.0"),
                rpe("8.0"),
                90,
                120,
            ),
            TemplateSlotSeed(
                "Разгибание ног", ("lever leg extension",), 3, 3, 12, 15, "12-15", rpe("8.0"), rpe("9.0"), 60, 90
            ),
            TemplateSlotSeed(
                "Сгибание ног",
                ("lever lying leg curl", "lever seated leg curl"),
                2,
                2,
                10,
                15,
                "10-15",
                rpe("8.0"),
                rpe("8.0"),
                60,
                90,
            ),
            TemplateSlotSeed(
                "Подъем на икры", ("lever standing calf raise",), 4, 4, 10, 20, "10-20", rpe("8.0"), rpe("9.0"), 60, 60
            ),
            TemplateSlotSeed(
                "Планка / dead bug", ("front plank", "dead bug"), 2, 3, None, None, "time or 8-12", None, None, 45, 60
            ),
        ),
    ),
    WorkoutTemplateSeed(
        code="upper_a",
        title="Верх A",
        weekday=2,
        focus="спина + бицепс + задняя дельта",
        description="Pull-focused upper-body session.",
        slots=(
            TemplateSlotSeed(
                "Тяга сверху / подтягивания",
                ("cable wide grip lat pulldown", "cable pulldown"),
                4,
                4,
                6,
                12,
                "6-12",
                rpe("8.0"),
                rpe("8.0"),
                120,
                120,
            ),
            TemplateSlotSeed(
                "Горизонтальная тяга сидя",
                ("cable seated row", "lever seated row"),
                4,
                4,
                8,
                12,
                "8-12",
                rpe("8.0"),
                rpe("8.0"),
                90,
                120,
            ),
            TemplateSlotSeed(
                "Тяга гантели одной рукой",
                ("dumbbell one arm row",),
                3,
                3,
                10,
                12,
                "10-12",
                rpe("8.0"),
                rpe("8.0"),
                90,
                90,
            ),
            TemplateSlotSeed(
                "Face pull / reverse fly",
                ("cable face pull", "lever reverse fly"),
                3,
                3,
                12,
                20,
                "12-20",
                rpe("8.0"),
                rpe("8.0"),
                60,
                60,
            ),
            TemplateSlotSeed(
                "Сгибание на бицепс",
                ("dumbbell biceps curl", "ez barbell curl"),
                3,
                3,
                8,
                12,
                "8-12",
                rpe("8.0"),
                rpe("8.0"),
                60,
                90,
            ),
            TemplateSlotSeed(
                "Hammer curl", ("dumbbell hammer curl",), 2, 3, 10, 15, "10-15", rpe("8.0"), rpe("8.0"), 60, 60
            ),
        ),
    ),
    WorkoutTemplateSeed(
        code="rest_wednesday",
        title="Восстановление",
        weekday=3,
        focus="восстановление / прогулка / мобильность",
        description="Rest day.",
        slots=(),
    ),
    WorkoutTemplateSeed(
        code="legs_b",
        title="Ноги B",
        weekday=4,
        focus="задняя поверхность бедра + ягодицы + икры",
        description="Hamstring-focused lower-body session without hip thrust or glute bridge.",
        slots=(
            TemplateSlotSeed(
                "Румынская тяга",
                ("barbell romanian deadlift", "dumbbell romanian deadlift"),
                4,
                4,
                6,
                10,
                "6-10",
                rpe("7.5"),
                rpe("8.5"),
                120,
                180,
            ),
            TemplateSlotSeed(
                "Жим ногами высокой постановкой",
                ("sled 45 degrees leg press", "lever leg press"),
                4,
                4,
                8,
                12,
                "8-12",
                rpe("8.0"),
                rpe("8.0"),
                90,
                120,
            ),
            TemplateSlotSeed(
                "Сгибание ног",
                ("lever lying leg curl", "lever seated leg curl"),
                3,
                3,
                10,
                15,
                "10-15",
                rpe("8.0"),
                rpe("9.0"),
                60,
                90,
            ),
            TemplateSlotSeed(
                "Обратные выпады",
                ("dumbbell reverse lunge",),
                3,
                3,
                8,
                12,
                "8-12 each leg",
                rpe("8.0"),
                rpe("8.0"),
                90,
                90,
            ),
            TemplateSlotSeed(
                "Гиперэкстензия 45°", ("hyperextension",), 3, 3, 10, 15, "10-15", rpe("8.0"), rpe("8.0"), 60, 90
            ),
            TemplateSlotSeed(
                "Подъем на икры", ("lever standing calf raise",), 4, 4, 12, 20, "12-20", rpe("8.0"), rpe("9.0"), 60, 60
            ),
            TemplateSlotSeed(
                "Side plank / Pallof press",
                ("side plank", "cable pallof press"),
                2,
                3,
                None,
                None,
                "time or 10-12",
                None,
                None,
                45,
                60,
            ),
        ),
    ),
    WorkoutTemplateSeed(
        code="boxing",
        title="Бокс",
        weekday=5,
        focus="техника / кондиционирование",
        description="Boxing technique and conditioning day.",
        slots=(),
    ),
    WorkoutTemplateSeed(
        code="upper_b",
        title="Верх B",
        weekday=6,
        focus="грудь + плечи + трицепс",
        description="Push-focused upper-body session with shoulder balance work.",
        slots=(
            TemplateSlotSeed(
                "Жим лежа / chest press",
                ("dumbbell bench press", "barbell bench press", "lever chest press"),
                4,
                4,
                6,
                10,
                "6-10",
                rpe("8.0"),
                rpe("8.0"),
                120,
                120,
            ),
            TemplateSlotSeed(
                "Наклонный жим гантелей",
                ("dumbbell incline bench press",),
                3,
                3,
                8,
                12,
                "8-12",
                rpe("8.0"),
                rpe("8.0"),
                90,
                120,
            ),
            TemplateSlotSeed(
                "Face pull / легкая тяга", ("cable face pull",), 2, 3, 12, 15, "12-15", rpe("7.0"), rpe("7.0"), 60, 90
            ),
            TemplateSlotSeed(
                "Жим гантелей сидя",
                ("dumbbell seated shoulder press",),
                2,
                3,
                6,
                10,
                "6-10",
                rpe("7.5"),
                rpe("8.0"),
                90,
                120,
            ),
            TemplateSlotSeed(
                "Подъемы в стороны",
                ("dumbbell lateral raise", "cable lateral raise"),
                3,
                3,
                12,
                20,
                "12-20",
                rpe("8.0"),
                rpe("9.0"),
                60,
                60,
            ),
            TemplateSlotSeed(
                "Трицепс pushdown", ("cable triceps pushdown",), 3, 3, 10, 15, "10-15", rpe("8.0"), rpe("8.0"), 60, 60
            ),
            TemplateSlotSeed(
                "Разгибание трицепса над головой",
                ("cable overhead triceps extension",),
                2,
                2,
                10,
                15,
                "10-15",
                rpe("8.0"),
                rpe("8.0"),
                60,
                60,
            ),
        ),
    ),
)


def project_weekday(value: date) -> int:
    return value.isoweekday() % 7


def get_template_seed_for_date(value: date) -> WorkoutTemplateSeed:
    weekday = project_weekday(value)
    for seed in DEFAULT_TEMPLATE_SEEDS:
        if seed.weekday == weekday:
            return seed
    raise ValueError(f"No template seed configured for weekday {weekday}")


def seed_workout_templates(session: Session) -> SeedTemplatesStats:
    templates_seeded = 0
    exercises_seeded = 0
    for seed in DEFAULT_TEMPLATE_SEEDS:
        template = session.scalars(select(WorkoutTemplate).where(WorkoutTemplate.code == seed.code)).one_or_none()
        if template is None:
            template = WorkoutTemplate(
                code=seed.code, title=seed.title, weekday=seed.weekday, focus=seed.focus, description=seed.description
            )
            session.add(template)
        else:
            template.title = seed.title
            template.weekday = seed.weekday
            template.focus = seed.focus
            template.description = seed.description
            template.template_exercises.clear()

        for index, slot in enumerate(seed.slots, start=1):
            template.template_exercises.append(
                TemplateExercise(
                    exercise=_find_first_exercise(session, slot.exercise_names),
                    slot_name=slot.slot_name,
                    order_index=index,
                    planned_sets_min=slot.planned_sets_min,
                    planned_sets_max=slot.planned_sets_max,
                    reps_min=slot.reps_min,
                    reps_max=slot.reps_max,
                    reps_text=slot.reps_text,
                    rpe_min=slot.rpe_min,
                    rpe_max=slot.rpe_max,
                    rest_seconds_min=slot.rest_seconds_min,
                    rest_seconds_max=slot.rest_seconds_max,
                    notes=slot.notes,
                )
            )
            exercises_seeded += 1
        templates_seeded += 1

    session.commit()
    return SeedTemplatesStats(templates_seeded=templates_seeded, exercises_seeded=exercises_seeded)


def _find_first_exercise(session: Session, names: tuple[str, ...]) -> Exercise | None:
    for name in names:
        exercise = session.scalars(
            select(Exercise).where(Exercise.name == name, Exercise.curation_status != "avoid")
        ).one_or_none()
        if exercise is not None:
            return exercise
    return None
