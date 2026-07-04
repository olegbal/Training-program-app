import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.exercise import Exercise


@dataclass(frozen=True)
class ImportStats:
    created: int = 0
    updated: int = 0


def build_media_url(path: str | None, raw_base: str | None = None) -> str | None:
    if not path:
        return None
    base = raw_base or get_settings().raw_media_base
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def map_dataset_exercise(item: dict[str, Any], raw_base: str | None = None) -> dict[str, Any]:
    source_id = str(item["id"])
    image_path = item.get("image")
    gif_path = item.get("gif_url")
    name = str(item["name"])
    is_avoided = _is_avoided_exercise(name)

    return {
        "source_id": source_id,
        "name": name,
        "ru_name": item.get("ru_name"),
        "body_part": item.get("body_part"),
        "target": item.get("target") or item.get("muscle_group"),
        "secondary_muscles": _as_string_list(item.get("secondary_muscles")),
        "equipment": item.get("equipment"),
        "movement_pattern": item.get("movement_pattern"),
        "difficulty": item.get("difficulty"),
        "image_path": image_path,
        "gif_path": gif_path,
        "image_url": build_media_url(image_path, raw_base),
        "gif_url": build_media_url(gif_path, raw_base),
        "instructions": item.get("instructions"),
        "instruction_steps": _as_string_list(item.get("instruction_steps")) if item.get("instruction_steps") else None,
        "curation_status": "avoid" if is_avoided else item.get("curation_status", "unreviewed"),
        "avoid_reason": "Avoid as a main exercise for this user." if is_avoided else item.get("avoid_reason"),
    }


def import_exercise_file(session: Session, input_path: Path) -> ImportStats:
    records = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Exercise dataset must be a JSON array")

    created = 0
    updated = 0
    for item in records:
        if not isinstance(item, dict):
            raise ValueError("Each exercise record must be a JSON object")

        values = map_dataset_exercise(item)
        existing = session.scalars(select(Exercise).where(Exercise.source_id == values["source_id"])).one_or_none()
        if existing is None:
            session.add(Exercise(**values))
            created += 1
        else:
            for key, value in values.items():
                setattr(existing, key, value)
            updated += 1

    session.commit()
    return ImportStats(created=created, updated=updated)


def _as_string_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _is_avoided_exercise(name: str) -> bool:
    normalized = name.casefold()
    return "hip thrust" in normalized or "glute bridge" in normalized
