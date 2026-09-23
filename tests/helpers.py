"""Изолированные тестовые каталоги внутри проекта."""

import shutil
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4


@contextmanager
def temporary_directory():
    """Создать каталог с наследуемыми правами доступа Windows."""
    root = Path(__file__).resolve().parents[1] / ".test-data"
    root.mkdir(exist_ok=True)
    path = root / uuid4().hex
    path.mkdir()
    try:
        yield str(path)
    finally:
        if path.resolve().parent != root.resolve():
            raise ValueError("Тестовый каталог вышел за пределы проекта.")
        shutil.rmtree(path)
