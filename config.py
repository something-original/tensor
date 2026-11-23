import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
root_dir = Path(__file__).resolve().parent

DB_USER = os.getenv("DB_USER", "tensor")
DB_PWD = os.getenv("DB_PWD", "tensor")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3333"))
DB_NAME = os.getenv("DB_NAME", "tensor")

DB_URL = f"postgresql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

FILE_PATH = os.getenv("FILE_PATH", "data/people.json")
FILE_PATH = os.path.join(root_dir, FILE_PATH)
