"""Точка входа для запуска приложения командой ``python main.py``."""

import sys
from pathlib import Path

# Добавляем src/ в путь импорта, чтобы приложение запускалось
# без предварительной установки пакета в окружение.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from tensor.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
