from __future__ import annotations

from .base import NamedEntity


class Category(NamedEntity):
    """Тематическая категория заметок."""

    def __init__(self, entity_id: int, name: str) -> None:
        super().__init__(entity_id, name)
