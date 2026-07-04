from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.workout_validator import WorkoutValidator

router = APIRouter(prefix="/ai", tags=["ai"])


class AiPlaceholderResponse(BaseModel):
    status: str = "placeholder"
    action: str
    message: str


class WorkoutValidationRequest(BaseModel):
    day_type: str | None = None
    exercises: list[dict[str, Any]] = Field(default_factory=list)
    weekly_templates: list[dict[str, Any]] = Field(default_factory=list)


class WorkoutValidationResponse(BaseModel):
    valid: bool
    warnings: list[str]


@router.post("/generate-workout", response_model=AiPlaceholderResponse)
def generate_workout() -> AiPlaceholderResponse:
    return _placeholder("generate-workout")


@router.post("/replace-exercise", response_model=AiPlaceholderResponse)
def replace_exercise() -> AiPlaceholderResponse:
    return _placeholder("replace-exercise")


@router.post("/explain-technique", response_model=AiPlaceholderResponse)
def explain_technique() -> AiPlaceholderResponse:
    return _placeholder("explain-technique")


@router.post("/analyze-progress", response_model=AiPlaceholderResponse)
def analyze_progress() -> AiPlaceholderResponse:
    return _placeholder("analyze-progress")


@router.post("/validate-workout", response_model=WorkoutValidationResponse)
def validate_workout(payload: WorkoutValidationRequest) -> WorkoutValidationResponse:
    result = WorkoutValidator().validate(payload.model_dump())
    return WorkoutValidationResponse(**result)


def _placeholder(action: str) -> AiPlaceholderResponse:
    return AiPlaceholderResponse(
        action=action,
        message="AI generation is not enabled in the MVP; this endpoint is reserved for OpenClaw integration.",
    )
