from config import load_config
from db.db import *

import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aioschedule
from aiogram import Dispatcher, executor, exceptions
from datetime import datetime,timedelta
from dateutil.parser import parse

# -837922550 (pizza)
# -1001807538179 (ЧМ)
# -507540833 (ana)

config = load_config("bot.ini")
bot = Bot(token=config.tg_bot.token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def get_matches_for_tomorrow():
    tommorow_date = datetime.now() + timedelta(days=1)
    tommorow_date = tommorow_date.strftime("%B %d, %Y")

    matches_for_tomorrow = set()

    for match in fetchall("match_schedule", ["date", "match"]):
        if match["date"] is not None:
            try:
                match_date = parse(match["date"]).strftime("%B %d, %Y")
                if match_date == tommorow_date:
                    match_time = "{:d}:{:02d}".format(parse(match['date']).hour, parse(match['date']).minute)
                    match_message = " | ".join([match_time, match["match"]])
                    matches_for_tomorrow.add(match_message)
            except Exception as e:
                await bot.send_message(config.tg_bot.admin_id, f"Error: '{e}' from get_matches_for_tomorrow()")

    return matches_for_tomorrow


async def send_match_from_db():
    matches = await get_matches_for_tomorrow()
    for _chat_id in config.tg_bot.chat_ids.split("|"):
        if len(matches):
            try:
                new_line = "\n"
                await bot.send_message(chat_id = _chat_id, text = f"На завтра запланированы {len(matches)} матч(-а/-ей)⚽️: \n{new_line.join(list(matches))} \n Не забудь отправить отложенное сообщение с прогнозом к началу матча!")
                
                tommorow_date = datetime.now() + timedelta(days=1)
                tommorow_date = tommorow_date.strftime("%B %d, %Y")
                
                poll = await bot.send_poll(chat_id = _chat_id, question=f"Прогнозы на {tommorow_date}", options=["+", "-"], is_anonymous=False)

                await bot.pin_chat_message(chat_id = _chat_id, message_id = poll["message_id"])
            except Exception as e:
                await bot.send_message(config.tg_bot.admin_id, f"Error: '{e}' send_match_from_db()")


@dp.message_handler()
async def answer_to_user(message: types.Message):
    if str(message.chat.id) not in config.tg_bot.chat_ids.split("|"):
        try:
            await bot.send_message(config.tg_bot.admin_id, f"'{message.text}' from {message.from_user.id}|{message.from_user.username}")
            await bot.send_message(message.chat.id, "Пиши в общую группу")
            await bot.send_sticker(chat_id=message.chat.id, sticker="CAACAgIAAxkBAAEPA05jeVg2lRYmT17SH9idq7s0C-qfRAACGRYAAnq6yEt4ZLqr8JHp0CsE")
        except Exception as e:
            await bot.send_message(config.tg_bot.admin_id, f"Error: '{e}' answer_to_user()")


@dp.errors_handler(exception=exceptions.RetryAfter)
async def exception_handler(update: types.Update, exception: exceptions.RetryAfter):
    pass
    return True


async def on_startup(dp: Dispatcher):
	asyncio.create_task(scheduler())


async def scheduler():
    EVERYDAY_TIME = "10:00" # TODO: to config
    aioschedule.every().day.at(EVERYDAY_TIME).do(send_match_from_db)

    while 1:
        await aioschedule.run_pending()
        await asyncio.sleep(1) 


if __name__ == "__main__":

    try:
        executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
    finally:
        dp.storage.close()
        dp.storage.wait_closed()