"""Поиск и фильтрация коллекций заметок, адаптированные после ПР2."""

from collections.abc import Iterable

from catalog import Notebook, get_item
from models import Note


def add_note(
    book: Notebook, title: str, text: str, author_id: int,
    project_id: int, category_id: int,
) -> Note:
    """Создать связанную заметку через каталог."""
    return book.add_note(title, text, author_id, project_id, category_id)


def find_notes(
    notes: Iterable[Note], query: str = "", *,
    project_id: int | None = None, category_id: int | None = None,
    author_id: int | None = None, archived: bool | None = None,
) -> list[Note]:
    """Совместить текстовый поиск, фильтры и сортировку по названию."""
    query = query.strip().casefold()
    found = (
        note for note in notes
        if query in (note.title + " " + note.text).casefold()
        and (project_id is None or note.project.id == project_id)
        and (category_id is None or note.category.id == category_id)
        and (author_id is None or note.author.id == author_id)
        and (archived is None or note.archived == archived)
    )
    return sorted(found, key=lambda note: (note.title.casefold(), note.id))


def archive_note(book: Notebook, note_id: int) -> None:
    """Адаптер функции ПР2 к методу объекта ПР3."""
    get_item(book.notes, note_id).archive()
