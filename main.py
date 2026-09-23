"""Русское консольное меню и точка входа приложения."""

import argparse
from collections.abc import Iterable
from copy import deepcopy
from pathlib import Path

from catalog import Notebook, get_item
from examples.demo import create_demo
from notes import add_note, archive_note, find_notes
from storage import StorageError, load_data, save_data
from utils import input_int

ROOT = Path(__file__).resolve().parent
MENU = """
СИСТЕМА ХРАНЕНИЯ ИССЛЕДОВАТЕЛЬСКИХ ЗАМЕТОК
1. Все заметки             2. Создать заметку
3. Поиск и фильтры         4. Прочитать заметку
5. Редактировать заметку   6. Архив / восстановление
7. Удалить заметку         8. Исследователи, проекты, категории
9. Статистика              0. Выход
"""


def show(items: Iterable[object]) -> None:
    """Печатать объекты с помощью полиморфного __str__."""
    found = False
    for item in items:
        found = True
        print(item)
    if not found:
        print("Записей нет.")


def choose(items: dict, label: str) -> int:
    """Показать доступные объекты и проверить выбранный ID."""
    if not items:
        raise ValueError(f"Сначала добавьте запись: {label} (пункт 8).")
    show(items.values())
    item_id = input_int(f"{label}, ID: ")
    get_item(items, item_id)
    return item_id


def optional_id(label: str) -> int | None:
    value = input(f"{label}, ID (Enter = все): ").strip()
    if not value:
        return None
    result = int(value)
    if result <= 0:
        raise ValueError("ID должен быть положительным.")
    return result


def read_text() -> str:
    """Прочитать многострочную заметку до строки с одной точкой."""
    print("Текст заметки (одна точка на отдельной строке завершает ввод):")
    lines = []
    while True:
        line = input()
        if line == ".":
            return "\n".join(lines)
        lines.append(line)


def catalogs(book: Notebook) -> bool:
    """Просмотр, добавление, переименование и удаление справочников."""
    kind = input("1 Исследователи | 2 Проекты | 3 Категории: ").strip()
    names = {"1": "researchers", "2": "projects", "3": "categories"}
    if kind not in names:
        raise ValueError("Неизвестный справочник.")
    items = getattr(book, names[kind])
    show(items.values())
    action = input("1 Добавить | 2 Изменить | 3 Удалить | "
                   "4 Архив проекта | Enter Назад: ").strip()
    if not action:
        return False
    if action == "1":
        name = input("Имя / название: ")
        if kind == "1":
            book.add_researcher(name, input("Email: "))
        elif kind == "2":
            book.add_project(name, choose(book.researchers, "Владелец"))
        else:
            book.add_category(name)
        return True
    if action not in {"2", "3", "4"}:
        raise ValueError("Неизвестное действие.")
    item_id = choose(items, "Запись")
    item = items[item_id]
    if action == "3":
        if input("Для удаления введите ДА: ").strip() != "ДА":
            return False
        book.delete(names[kind], item_id)
    elif action == "4":
        if kind != "2":
            raise ValueError("Архив предусмотрен только для проектов.")
        item.restore() if item.archived else item.archive()
    else:
        item.name = input("Новое имя / название: ")
        if kind == "1":
            item.email = input("Новый email: ")
        elif kind == "2":
            item.owner = get_item(
                book.researchers, choose(book.researchers, "Владелец"))
    return True


def execute(book: Notebook, choice: str) -> bool:
    """Выполнить команду; вернуть признак изменения данных."""
    if choice == "1":
        show(find_notes(book.notes.values()))
    elif choice == "2":
        author_id = choose(book.researchers, "Автор")
        project_id = choose(book.projects, "Проект")
        category_id = choose(book.categories, "Категория")
        title = input("Название: ")
        note = add_note(book, title, read_text(), author_id,
                        project_id, category_id)
        print(f"Создана заметка #{note.id}.")
        return True
    elif choice == "3":
        query = input("Текст поиска (Enter = любой): ")
        project = optional_id("Проект")
        category = optional_id("Категория")
        author = optional_id("Автор")
        status = input("Статус: 1 Активные | 2 Архив | Enter Все: ").strip()
        if status not in {"", "1", "2"}:
            raise ValueError("Неизвестный статус.")
        show(find_notes(
            book.notes.values(), query, project_id=project,
            category_id=category, author_id=author,
            archived={"": None, "1": False, "2": True}[status],
        ))
    elif choice in {"4", "5", "6", "7"}:
        note_id = choose(book.notes, "Заметка")
        note = book.notes[note_id]
        if choice == "4":
            print(note)
            print(f"Создана: {note.created_at}; изменена: {note.updated_at}")
            print(note.text)
            return False
        if choice == "5":
            title = input("Новое название: ")
            note.edit(title, read_text())
        elif choice == "6":
            if note.archived:
                note.restore()
            else:
                archive_note(book, note_id)
        else:
            if input("Для удаления введите ДА: ").strip() != "ДА":
                return False
            book.delete("notes", note_id)
        return True
    elif choice == "8":
        return catalogs(book)
    elif choice == "9":
        print(f"Исследователей: {len(book.researchers)}; "
              f"проектов: {len(book.projects)}; "
              f"категорий: {len(book.categories)}")
        archived = sum(note.archived for note in book.notes.values())
        print(f"Заметок: {len(book.notes)}; в архиве: {archived}")
        for category in book.categories.values():
            count = sum(n.category is category for n in book.notes.values())
            print(f"{category.name}: {count}")
    else:
        raise ValueError("Нет такого пункта меню.")
    return False


def main() -> int:
    """Каждое изменение сохраняется до принятия новой команды."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "data/notes.json",
                        help="Путь к JSON-хранилищу")
    parser.add_argument("--demo", action="store_true",
                        help="Показать пример без изменения данных")
    args = parser.parse_args()
    try:
        book = create_demo() if args.demo else load_data(args.data)
    except StorageError as error:
        print(f"{error}\nИсправьте файл или задайте другой путь через --data.")
        return 1
    if args.demo:
        show(find_notes(book.notes.values()))
        execute(book, "9")
        return 0
    print(f"Хранилище: {args.data.resolve()}")
    while True:
        try:
            print(MENU)
            choice = input("> ").strip()
            if choice == "0":
                return 0
            candidate = deepcopy(book)
            if execute(candidate, choice):
                save_data(args.data, candidate)
                book = candidate
                print("Сохранено.")
        except (ValueError, OSError) as error:
            print(f"Ошибка: {error}\nИзменения не применены.")
        except (EOFError, KeyboardInterrupt):
            print("\nРабота завершена. Данные доступны при следующем запуске.")
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
