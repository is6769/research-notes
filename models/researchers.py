from __future__ import annotations

from utils import validate_title

from .base import NamedEntity


class Researcher(NamedEntity):
    """Автор заметок и владелец исследовательских проектов."""

    def __init__(self, entity_id: int, name: str, email: str) -> None:
        super().__init__(entity_id, name)
        self.email = email

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        value = validate_title(value)
        parts = value.split("@")
        if len(parts) != 2 or not all(parts) or any(
            char.isspace() for char in value
        ):
            raise ValueError("Укажите email в формате имя@домен.")
        self._email = value

    def __str__(self) -> str:
        return f"{super().__str__()} <{self.email}>"
