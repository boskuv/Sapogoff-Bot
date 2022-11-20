"""Парсер конфигурации бота"""
import configparser
from dataclasses import dataclass


@dataclass
class TgBot:
    token: str
    chat_ids: str
    admin_id: str


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path)

    tg_bot = config["tg_bot"]

    return Config(
        tg_bot=TgBot(
            token=tg_bot.get("token"),
            chat_ids=tg_bot.get("chat_ids"),
            admin_id=tg_bot.get("admin_id"),
        ),
    )
