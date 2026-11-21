import sys
from contextlib import asynccontextmanager
from logging import INFO, Formatter, Logger, StreamHandler, getLogger

import uvicorn
from fastapi import FastAPI

from config import DB_URL, FILE_PATH, HOST, PORT
from src.tensor import check_init_database


def setup_logger(name: str | None = None, level=INFO) -> Logger:

    logger = getLogger(name)
    logger.setLevel(level)

    console_handler = StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    formatter = Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


@asynccontextmanager
async def lifespan(app):
    await check_init_database(DB_URL, FILE_PATH)
    yield


app = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    logger = setup_logger()
    uvicorn.run("main:app", host=HOST, port=PORT)
