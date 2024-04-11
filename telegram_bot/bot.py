import io
import json
import logging
import time
from typing import Optional

import ast
# import asyncio
import pandas as pd
import numpy as np

import requests
from requests.exceptions import HTTPError, ConnectionError

from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import BufferedInputFile
from aiogram.filters.command import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# from aiohttp import web
# from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config_reader import config
import message_texts


bot = Bot(token=config.bot_token)
dp = Dispatcher(bot=bot)


class NumbersCallbackFactory(CallbackData, prefix="fabnum"):
    action: str
    value: Optional[int] = None


class PredictorsCallbackFactory(CallbackData, prefix="fabpred"):
    action: str
    value: Optional[int] = None


def create_logger():
    """Logger initialization"""
    logger = logging.getLogger()
    if logger.hasHandlers():
        return logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] {%(pathname)s:%(lineno)d} %(name)s : %(message)s"
    )
    file_handler = logging.StreamHandler()
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


logger = create_logger()
logger.info("Creating a logger for Main")


def load_feedback_ratings():
    """Feedback data loader"""
    try:
        with open(config.json_file, "r") as file:
            feedback_ratings = json.load(file)
    except FileNotFoundError:
        feedback_ratings = {}

    return feedback_ratings


feedback_ratings = load_feedback_ratings()


@dp.message(Command("start"))
async def cmd_start(
    message: types.Message,
) -> None:
    """Handle /start command"""
    uid = message.from_user.id
    if uid not in feedback_ratings:
        feedback_ratings[uid] = {}
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text=message_texts.allowed_requests[0]))
    builder.row(types.KeyboardButton(text=message_texts.allowed_requests[1]))
    builder.row(types.KeyboardButton(text=message_texts.allowed_requests[2]))
    builder.row(types.KeyboardButton(text=message_texts.allowed_requests[3]))
    builder.row(types.KeyboardButton(text=message_texts.allowed_requests[4]))
    try:
        response = requests.post(
            f"{config.webhook_host}/create_user/{message.from_user.id}"
        )
        response.raise_for_status()
        await message.answer(
            message_texts.start,
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
    except HTTPError or ConnectionError:
        await message.answer(message_texts.connection_error)


@dp.message(Command("help"))
@dp.message(F.text.lower() == message_texts.allowed_requests[0].lower())
async def cmd_help(
    message: types.Message,
) -> None:
    """Handle /help command"""
    await message.answer(
        message_texts.help,
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message(Command("ping"))
@dp.message(F.text.lower() == message_texts.allowed_requests[4].lower())
async def cmd_ping(
    message: types.Message,
) -> None:
    """Handle /ping command"""
    try:
        response = requests.get(f"{config.webhook_host}/ping")
        response.raise_for_status()
        await message.answer(response.text)
    except HTTPError or ConnectionError:
        await message.answer(message_texts.connection_error)


@dp.message(Command("predict"))
@dp.message(F.text.lower() == message_texts.allowed_requests[1].lower())
async def cmd_predict(
    message: types.Message,
) -> None:
    """Handle /predict command"""
    await message.answer(
        message_texts.predict,
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message(F.document)
async def make_predictions(
    message: types.Message,
) -> None:
    """Handle input documents"""
    response = None
    if message.document.mime_type == "text/csv":
        await message.answer(message_texts.processing)
        file_bytes = await bot.download(message.document)
        df = pd.read_csv(file_bytes, encoding="utf-8", sep=None, engine="python")
        try:
            response = requests.post(
                f"{config.webhook_host}/predict",
                json={
                    "vals": df.to_dict(orient="list"),
                    "user": message.from_user.username,
                },
            )
            response.raise_for_status()
            response_dict = ast.literal_eval(response.text)
            response_df = pd.DataFrame(response_dict.values())
            response_csv = response_df.to_csv(index=False)
            predictions = BufferedInputFile(
                io.BytesIO(response_csv.encode()).getvalue(), filename="predictions.csv"
            )
            await bot.send_document(
                message.chat.id, predictions, caption=message_texts.predictions
            )
        except HTTPError or ConnectionError:
            await message.answer(message_texts.connection_error)
    else:
        await message.answer(message_texts.invalid_format)


@dp.message(Command("feedback"))
@dp.message(F.text.lower() == message_texts.allowed_requests[2].lower())
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
    logger.info(f"Recieved new callback from user {user_name}: {callback.message}")
    rating = callback_data.value

    if uid not in feedback_ratings:
        feedback_ratings[uid] = {}

    feedback_ratings[uid][timestamp] = rating

    with open(config.json_file, "w") as file:
        json.dump(feedback_ratings, file)
    await callback.message.answer(message_texts.thanks)


@dp.message(Command("rating"))
@dp.message(F.text.lower() == message_texts.allowed_requests[3].lower())
async def feedback_stats(
    message: types.Message,
) -> None:
    """Handle /rating command"""
    try:
        with open(config.json_file, "r") as file:
            feedback_ratings = json.load(file)
            if feedback_ratings:
                n = 0
                summ = 0
                users = []
                for i in feedback_ratings:
                    for j in feedback_ratings[i].values():
                        users.append(i)
                        n += 1
                        summ += int(j)
                users = set(users)
                await message.answer(
                    message_texts.feedback_report.format(
                        len(feedback_ratings.keys()),
                        len(users),
                        np.round(summ / n if n > 0 else 0, 2),
                    )
                )
            else:
                await message.answer(message_texts.no_feedback)
    except FileNotFoundError:
        await message.answer(message_texts.no_feedback)


@dp.message(F.text)
async def not_allowed(
    message: types.Message,
) -> None:
    """Handle text not included in commands"""
    logger.info(
        f"Получено сообщение от пользователя {message.from_user.username}: {message.text}"
    )
    await message.answer(message_texts.invalid_cmd)


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(url=config.webhook_url)


async def on_shutdown(dp):
    await bot.delete_webhook()


def main():
    # if config.env_type == "local":
    dp.start_polling(bot)
    # else:
    #     dp.startup.register(on_startup)
    #     app = web.Application()
    #     webhook_requests_handler = SimpleRequestHandler(
    #         dispatcher=dp,
    #         bot=bot,
    #     )
    #     webhook_requests_handler.register(app, path=config.webhook_path)
    #     setup_application(app, dp, bot=bot)
    #     web.run_app(app, host="0.0.0.0", port=10000)


if __name__ == "__main__":
    main()
