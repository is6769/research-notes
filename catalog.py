"""Коллекции объектов и операции, затрагивающие несколько сущностей."""

from __future__ import annotations

from typing import TypeVar

from models import Category, NamedEntity, Note, Project, Researcher

T = TypeVar("T", bound=NamedEntity)


def next_id(items: dict[int, T]) -> int:
    """Выбрать свободный идентификатор в коллекции."""
    return max(items, default=0) + 1


def get_item(items: dict[int, T], item_id: int) -> T:
    """Найти объект либо сообщить о неизвестном идентификаторе."""
    try:
        return items[item_id]
    except KeyError as error:
        raise ValueError(f"Объект с ID {item_id} не найден.") from error


class Notebook:
    """Связанные коллекции объектов одного локального хранилища."""

    def __init__(self) -> None:
        self.researchers: dict[int, Researcher] = {}
        self.projects: dict[int, Project] = {}
        self.categories: dict[int, Category] = {}
        self.notes: dict[int, Note] = {}

    def add_researcher(self, name: str, email: str) -> Researcher:
        item = Researcher(next_id(self.researchers), name, email)
        if any(r.email.casefold() == item.email.casefold()
               for r in self.researchers.values()):
            raise ValueError("Исследователь с таким email уже существует.")
        self.researchers[item.id] = item
        return item

    def add_category(self, name: str) -> Category:
        item = Category(next_id(self.categories), name)
        if any(c.name.casefold() == item.name.casefold()
               for c in self.categories.values()):
            raise ValueError("Категория с таким названием уже существует.")
        self.categories[item.id] = item
        return item

    def add_project(self, name: str, owner_id: int) -> Project:
        item = Project(next_id(self.projects), name,
                       get_item(self.researchers, owner_id))
        self.projects[item.id] = item
        return item

    def add_note(
        self, title: str, text: str, author_id: int, project_id: int,
        category_id: int,
    ) -> Note:
        project = get_item(self.projects, project_id)
        if project.archived:
            raise ValueError("Нельзя добавлять заметки в архивный проект.")
        item = Note(
            next_id(self.notes), title, text,
            get_item(self.researchers, author_id), project,
            get_item(self.categories, category_id),
        )
        self.notes[item.id] = item
        return item

    def delete(self, collection: str, item_id: int) -> None:
        """Удалить объект, если на него не ссылаются другие объекты."""
        collections = {
            "notes": self.notes, "researchers": self.researchers,
            "projects": self.projects, "categories": self.categories,
        }
        if collection not in collections:
            raise ValueError("Неизвестная коллекция.")
        items = collections[collection]
        item = get_item(items, item_id)
        referenced = any(
            item is n.author or item is n.project or item is n.category
            for n in self.notes.values()
        ) or any(item is p.owner for p in self.projects.values())
        if referenced:
            raise ValueError("Объект используется: сначала удалите связи.")
        del items[item_id]
