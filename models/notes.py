from __future__ import annotations

from datetime import datetime

from utils import get_note_status, reading_minutes, validate_title

from .base import NamedEntity
from .categories import Category
from .projects import Project
from .researchers import Researcher


class Note(NamedEntity):
    """Заметка содержит ссылки на объекты автора, проекта и категории."""

    def __init__(
        self, entity_id: int, title: str, text: str,
        author: Researcher, project: Project, category: Category,
        archived: bool = False, created_at: str | None = None,
        updated_at: str | None = None,
    ) -> None:
        super().__init__(entity_id, title)
        if not isinstance(author, Researcher) or not isinstance(
            project, Project
        ) or not isinstance(category, Category):
            raise ValueError("Неверные связи заметки.")
        if type(archived) is not bool:
            raise ValueError("Состояние архива должно быть логическим.")
        self._text = validate_title(text)
        self.author = author
        self.project = project
        self.category = category
        self._archived = archived
        self.created_at = self._timestamp(created_at)
        self.updated_at = self._timestamp(updated_at or self.created_at)
        if self.updated_at < self.created_at:
            raise ValueError("Изменение не может быть раньше создания.")

    @staticmethod
    def _timestamp(value: str | None) -> str:
        if value is None:
            return datetime.now().isoformat(timespec="microseconds")
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is not None:
            raise ValueError("Ожидается локальное время без часового пояса.")
        return parsed.isoformat(timespec="microseconds")

    @property
    def title(self) -> str:
        return self.name

    @property
    def text(self) -> str:
        return self._text

    @property
    def archived(self) -> bool:
        return self._archived

    @property
    def minutes(self) -> int:
        return reading_minutes(len(self.text.split()))

    def edit(self, title: str, text: str) -> None:
        """Проверить оба поля до изменения объекта."""
        if self.archived or self.project.archived:
            raise ValueError("Для редактирования восстановите из архива.")
        title, text = validate_title(title), validate_title(text)
        self.name = title
        self._text = text
        self.updated_at = self._timestamp(None)

    def archive(self) -> None:
        self._archived = True
        self.updated_at = self._timestamp(None)

    def restore(self) -> None:
        if self.project.archived:
            raise ValueError("Сначала восстановите проект из архива.")
        self._archived = False
        self.updated_at = self._timestamp(None)

    def __str__(self) -> str:
        return (f"{self.id}. {self.title} | {self.author.name} | "
                f"{self.project.name} / {self.category.name} | "
                f"{get_note_status(self.archived)} | {self.minutes} мин.")
