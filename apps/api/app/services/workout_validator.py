from decimal import Decimal, InvalidOperation
from typing import Any


class WorkoutValidator:
    avoid_terms = ("hip thrust", "glute bridge")
    hinge_terms = ("romanian deadlift", "stiff leg deadlift", "hyperextension", "good morning")
    push_patterns = {"bench_press", "incline_press", "overhead_press", "triceps_extension"}
    pull_patterns = {"vertical_pull", "horizontal_pull", "rear_delt", "biceps_curl"}

    def validate(self, workout: dict[str, Any]) -> dict[str, Any]:
        warnings: list[str] = []
        blocking_warnings: list[str] = []
        exercises = list(workout.get("exercises") or [])

        self._check_avoided_primary_exercises(exercises, blocking_warnings)
        self._check_failure_programming(exercises, warnings)
        self._check_rpe_ranges(exercises, warnings)
        self._check_legs_b_lower_back_load(str(workout.get("day_type") or ""), exercises, warnings)
        self._check_heavy_hip_hinges(exercises, warnings)
        self._check_weekly_coverage(workout, warnings)

        all_warnings = [*blocking_warnings, *warnings]
        return {"valid": not blocking_warnings, "warnings": all_warnings}

    def _check_avoided_primary_exercises(self, exercises: list[dict[str, Any]], warnings: list[str]) -> None:
        for item in exercises:
            name = _lower_name(item)
            if item.get("is_primary") and any(term in name for term in self.avoid_terms):
                warnings.append(f"{item.get('name')} is marked avoid and should not be a primary exercise.")

    def _check_failure_programming(self, exercises: list[dict[str, Any]], warnings: list[str]) -> None:
        hard_sets = 0
        for item in exercises:
            rpe = _decimal(item.get("rpe"))
            if rpe is not None and rpe >= Decimal("10"):
                hard_sets += 1
        if exercises and hard_sets == len(exercises):
            warnings.append("Every exercise is programmed at failure; keep hard work controlled instead.")

    def _check_rpe_ranges(self, exercises: list[dict[str, Any]], warnings: list[str]) -> None:
        for item in exercises:
            rpe = _decimal(item.get("rpe"))
            if rpe is None:
                continue
            pattern = str(item.get("movement_pattern") or "")
            compound_patterns = self.push_patterns | self.pull_patterns | {"squat", "hinge", "leg_press"}
            if pattern in compound_patterns and rpe > Decimal("9.5"):
                warnings.append(f"{item.get('name')} is above the usual compound RPE range.")
            if pattern in {"lateral_raise", "rear_delt", "biceps_curl", "triceps_extension"} and rpe > Decimal("9.5"):
                warnings.append(f"{item.get('name')} is above the usual isolation RPE range.")

    def _check_legs_b_lower_back_load(
        self,
        day_type: str,
        exercises: list[dict[str, Any]],
        warnings: list[str],
    ) -> None:
        if day_type != "legs_b":
            return
        names = [_lower_name(item) for item in exercises]
        has_rdl = any("romanian deadlift" in name or "stiff leg deadlift" in name for name in names)
        has_hyperextension = any("hyperextension" in name for name in names)
        if has_rdl and has_hyperextension:
            warnings.append(
                "Legs B includes Romanian deadlift and hyperextension; "
                "keep hyperextension at RPE 7-8 if lower back is fatigued."
            )

    def _check_heavy_hip_hinges(self, exercises: list[dict[str, Any]], warnings: list[str]) -> None:
        heavy_hinges = [
            item
            for item in exercises
            if str(item.get("movement_pattern") or "") == "hinge"
            and any(term in _lower_name(item) for term in self.hinge_terms)
            and (_decimal(item.get("rpe")) or Decimal("0")) >= Decimal("7.5")
        ]
        if len(heavy_hinges) > 1:
            warnings.append("Workout includes more than one heavy hip hinge; manage lower-back fatigue carefully.")

    def _check_weekly_coverage(self, workout: dict[str, Any], warnings: list[str]) -> None:
        templates = list(workout.get("weekly_templates") or [])
        if not templates:
            return

        leg_days = [template for template in templates if str(template.get("day_type") or "").startswith("legs")]
        if len(leg_days) < 2:
            warnings.append("Default week has fewer than two leg training days.")

        patterns = {
            str(exercise.get("movement_pattern") or "")
            for template in templates
            for exercise in list(template.get("exercises") or [])
        }
        if not (patterns & self.push_patterns) or not (patterns & self.pull_patterns):
            warnings.append("Upper body template should include both pushing and pulling coverage.")

        core_count = sum(1 for pattern in patterns if pattern in {"anti_extension", "anti_rotation", "core_stability"})
        if core_count < 2:
            warnings.append("Core should appear at least twice per week.")

        for day_type in ("legs_a", "legs_b"):
            day = next((template for template in templates if template.get("day_type") == day_type), None)
            day_patterns = {
                str(exercise.get("movement_pattern") or "") for exercise in list((day or {}).get("exercises") or [])
            }
            if "calf_raise" not in day_patterns:
                warnings.append(f"{day_type} should include calf work.")


def _lower_name(item: dict[str, Any]) -> str:
    return str(item.get("name") or item.get("slot_name") or "").lower()


def _decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value).split("-")[-1])
    except (InvalidOperation, ValueError):
        return None
