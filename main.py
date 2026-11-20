from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from config import DB_URL, HOST, PORT
from src.tensor import check_init_database


@asynccontextmanager
async def lifespan(app):
    await check_init_database(DB_URL)
    yield


app = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT)
