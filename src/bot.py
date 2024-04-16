import time

from typing import Optional

from loguru import logger
from logger import init_logging

from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

import utils.message_texts as message_texts
from utils.tracker import tracker
from config_reader import config

init_logging(json_logging=True, plain_log_level="INFO")

bot = Bot(token=config.bot_token)
dp = Dispatcher(bot=bot)


class NumbersCallbackFactory(CallbackData, prefix="fabnum"):
    action: str
    value: Optional[int] = None


class PredictorsCallbackFactory(CallbackData, prefix="fabpred"):
    action: str
    value: Optional[int] = None


@dp.message(Command("start"))
@dp.message(F.text.lower() == "start")
async def cmd_start(
    message: types.Message,
) -> None:
    """Handle /start command"""
    logger.info("User action", action="start")
    uid = message.from_user.id
    if uid not in tracker.feedback_ratings:
        tracker.feedback_ratings[uid] = {}
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="start"))
    builder.row(types.KeyboardButton(text="feedback"))

    await message.answer(
        message_texts.start,
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@dp.message(Command("feedback"))
@dp.message(F.text.lower() == "feedback")
async def feedback(
    message: types.Message,
) -> None:
    """Handle /feedback command"""
    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        builder.button(
            text=str(i),
            callback_data=NumbersCallbackFactory(action="feedback", value=i),
        )
    builder.adjust(5)
    await message.answer(
        message_texts.feedback,
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@dp.callback_query(NumbersCallbackFactory.filter())
async def callbacks_num_change_fab(
    callback: types.CallbackQuery,
    callback_data: NumbersCallbackFactory,
) -> None:
    """Handle callbacks from user"""
    user_name = callback.from_user.username
    uid = callback.from_user.id
    timestamp = str(int(time.time()))
    logger.info(f"Recieved new callback from user {user_name}: {callback_data.value}")
    rating = callback_data.value

    if uid not in tracker.feedback_ratings:
        tracker.feedback_ratings[uid] = {}

    tracker.feedback_ratings[uid][timestamp] = rating

    tracker._dump_feedback_ratings()

    await callback.message.answer(message_texts.thanks)


@dp.message(~F.text.in_({"start", "feedback"}))
async def not_allowed(
    message: types.Message,
) -> None:
    """Handle text not included in commands"""
    logger.info(
        f"Получено сообщение от пользователя: {message.text}",
        username=message.from_user.username
    )
    await message.answer(message_texts.invalid_cmd)

if __name__ == "__main__":
    logger.info("Bot started running")
    dp.run_polling(bot)
