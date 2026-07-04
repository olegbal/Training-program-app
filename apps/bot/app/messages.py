from typing import Any


def format_today_message(workout: dict[str, Any]) -> str:
    session = workout["session"]
    lines = [
        f"Сегодня: {session['title']}",
        str(session.get("focus") or ""),
        "",
        "Упражнения:",
    ]
    for index, item in enumerate(workout.get("exercises", []), start=1):
        sets = item.get("planned_sets") or "-"
        reps = item.get("planned_reps") or "-"
        lines.append(f"{index}. {item['slot_name']} — {sets} x {reps}")
    return "\n".join(line for line in lines if line != "")


def access_denied_message() -> str:
    return "Доступ закрыт."


def start_message() -> str:
    return "Привет. Это личный трекер тренировок: план на сегодня, подходы, история и замены упражнений."


def history_message() -> str:
    return "Журнал тренировок доступен в Mini App."


def help_message() -> str:
    return "Команды: /start, /today, /history, /help. Основная работа идёт в Telegram Mini App."
