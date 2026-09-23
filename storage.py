"""JSON: восстановление ссылок на объекты и атомарная запись файла."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from catalog import Notebook, get_item
from models import Category, Note, Project, Researcher


class StorageError(ValueError):
    """Ошибка чтения, формата либо записи хранилища."""


def to_data(book: Notebook) -> dict[str, Any]:
    """Заменить ссылки на объекты идентификаторами для JSON."""
    return {
        "version": 1,
        "researchers": [
            {"id": r.id, "name": r.name, "email": r.email}
            for r in book.researchers.values()
        ],
        "categories": [
            {"id": c.id, "name": c.name} for c in book.categories.values()
        ],
        "projects": [
            {"id": p.id, "name": p.name, "owner_id": p.owner.id,
             "archived": p.archived} for p in book.projects.values()
        ],
        "notes": [
            {"id": n.id, "title": n.title, "text": n.text,
             "author_id": n.author.id, "project_id": n.project.id,
             "category_id": n.category.id, "archived": n.archived,
             "created_at": n.created_at, "updated_at": n.updated_at}
            for n in book.notes.values()
        ],
    }


def migrate_pr2(data: list) -> dict[str, Any]:
    """Связать старые заметки с явно обозначенными сущностями импорта."""
    book = Notebook()
    author = book.add_researcher("Автор из ПР2", "pr2@local")
    category = book.add_category("Без категории (ПР2)")
    project = book.add_project("Импорт ПР2", author.id)
    for row in data:
        if not isinstance(row, dict):
            raise ValueError("Неверная запись ПР2.")
        note = Note(row["id"], row["title"], row["text"], author,
                    project, category, row["archived"])
        if note.id in book.notes:
            raise ValueError("Повторяющийся ID заметки ПР2.")
        book.notes[note.id] = note
    return to_data(book)


def from_data(data: Any) -> Notebook:
    """Проверить схему JSON и восстановить граф объектов."""
    try:
        if isinstance(data, list):
            data = migrate_pr2(data)
        if not isinstance(data, dict) or type(data["version"]) is not int:
            raise ValueError("Отсутствует версия формата.")
        if data["version"] != 1:
            raise ValueError("Неподдерживаемая версия формата.")
        book = Notebook()
        for key in ("researchers", "categories", "projects", "notes"):
            if not isinstance(data[key], list):
                raise ValueError(f"{key}: ожидается список.")
            collection = getattr(book, key)
            for row in data[key]:
                if not isinstance(row, dict):
                    raise ValueError("Ожидается объект JSON.")
                if key == "researchers":
                    item = Researcher(row["id"], row["name"], row["email"])
                    if any(r.email.casefold() == item.email.casefold()
                           for r in collection.values()):
                        raise ValueError("Повторяющийся email.")
                elif key == "categories":
                    item = Category(row["id"], row["name"])
                    if any(c.name.casefold() == item.name.casefold()
                           for c in collection.values()):
                        raise ValueError("Повторяющаяся категория.")
                elif key == "projects":
                    item = Project(
                        row["id"], row["name"],
                        _reference(book.researchers, row["owner_id"]),
                        row["archived"],
                    )
                else:
                    item = Note(
                        row["id"], row["title"], row["text"],
                        _reference(book.researchers, row["author_id"]),
                        _reference(book.projects, row["project_id"]),
                        _reference(book.categories, row["category_id"]),
                        row["archived"], row["created_at"], row["updated_at"],
                    )
                if item.id in collection:
                    raise ValueError(f"Повторяющийся ID в {key}.")
                collection[item.id] = item
        return book
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        raise StorageError(f"Некорректные данные: {error}") from error


def _reference(items: dict, item_id: int) -> Any:
    if type(item_id) is not int or item_id <= 0:
        raise ValueError("Ссылка должна содержать положительный целый ID.")
    return get_item(items, item_id)


def load_data(path: Path) -> Notebook:
    """Отсутствующий файл означает новое пустое хранилище."""
    try:
        with path.open(encoding="utf-8-sig") as stream:
            return from_data(json.load(stream))
    except FileNotFoundError:
        return Notebook()
    except (OSError, ValueError) as error:
        raise StorageError(f"Не удалось прочитать {path}: {error}") from error


def save_data(path: Path, book: Notebook) -> None:
    """Записать проверенные данные через временный файл и os.replace."""
    temporary = None
    try:
        data = to_data(book)
        from_data(data)
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=path.name + ".", suffix=".tmp", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except (OSError, ValueError) as error:
        raise StorageError(f"Не удалось сохранить {path}: {error}") from error
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
