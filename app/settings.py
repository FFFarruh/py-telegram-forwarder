import logging

from pydantic import BaseSettings

logging.basicConfig(
    level=logging.INFO,
    format="[{asctime} - {name} - {levelname}]: {message}",
    style="{",
)


class Settings(BaseSettings):
    api_id: int
    api_hash: str
    target_id: int
    from_chat_ids: list
    db_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
