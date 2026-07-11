from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from app.api_client import TrainingApiClient
from app.config import BotSettings
from app.messages import access_denied_message, format_today_message, help_message, history_message, start_message

router = Router()


def mini_app_keyboard(settings: BotSettings) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть тренировку",
                    web_app=WebAppInfo(url=settings.mini_app_url),
                )
            ]
        ],
    )


def is_allowed(message: Message, settings: BotSettings) -> bool:
    if message.from_user is None:
        return False
    if not settings.telegram_allowed_user_ids:
        return False
    return message.from_user.id in settings.telegram_allowed_user_ids


async def answer_access_denied(message: Message) -> None:
    await message.answer(access_denied_message())


@router.message(Command("start"))
async def start(message: Message, settings: BotSettings) -> None:
    if not is_allowed(message, settings):
        await answer_access_denied(message)
        return
    await message.answer(start_message(), reply_markup=mini_app_keyboard(settings))


@router.message(Command("today"))
async def today(message: Message, settings: BotSettings) -> None:
    if not is_allowed(message, settings):
        await answer_access_denied(message)
        return
    try:
        async with TrainingApiClient(settings.api_url) as api:
            workout = await api.get_today_workout()
        text = format_today_message(workout)
    except Exception:
        text = "Не удалось загрузить тренировку из API. Открой Mini App и попробуй там."
    await message.answer(text, reply_markup=mini_app_keyboard(settings))


@router.message(Command("history"))
async def history(message: Message, settings: BotSettings) -> None:
    if not is_allowed(message, settings):
        await answer_access_denied(message)
        return
    await message.answer(history_message(), reply_markup=mini_app_keyboard(settings))


@router.message(Command("help"))
async def help_command(message: Message, settings: BotSettings) -> None:
    if not is_allowed(message, settings):
        await answer_access_denied(message)
        return
    await message.answer(help_message(), reply_markup=mini_app_keyboard(settings))
