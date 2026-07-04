from aiogram import Router
from aiogram.filters import Command
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, WebAppInfo

from app.config import BotSettings

router = Router()


def mini_app_keyboard(settings: BotSettings) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="Открыть тренировку",
                    web_app=WebAppInfo(url=settings.mini_app_url),
                )
            ]
        ],
        resize_keyboard=True,
    )


@router.message(Command("start"))
async def start(message: Message, settings: BotSettings) -> None:
    await message.answer(
        "Привет. Это личный трекер тренировок: план на сегодня, подходы, история и замены упражнений.",
        reply_markup=mini_app_keyboard(settings),
    )


@router.message(Command("today"))
async def today(message: Message, settings: BotSettings) -> None:
    await message.answer(
        "Сегодняшняя тренировка появится здесь после подключения workout API. Мини-приложение уже можно открыть.",
        reply_markup=mini_app_keyboard(settings),
    )


@router.message(Command("history"))
async def history(message: Message, settings: BotSettings) -> None:
    await message.answer(
        "Журнал тренировок будет доступен в Mini App после Phase 4.",
        reply_markup=mini_app_keyboard(settings),
    )


@router.message(Command("help"))
async def help_command(message: Message, settings: BotSettings) -> None:
    await message.answer(
        "Команды: /start, /today, /history, /help. Основная работа будет в Telegram Mini App.",
        reply_markup=mini_app_keyboard(settings),
    )
