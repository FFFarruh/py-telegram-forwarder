import logging

from pydantic import BaseSettings

logging.basicConfig(
    level=logging.INFO,
    format="[{asctime} - {name} - {levelname}]: {message}",
    style="{",
)


class Settings(BaseSettings):
    telegram_bot_token: str
    user_id: str
    from_chat_ids: list

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
