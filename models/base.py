from __future__ import annotations

from utils import validate_title


class NamedEntity:
    """Общая сущность с идентификатором и проверяемым именем."""

    def __init__(self, entity_id: int, name: str) -> None:
        if type(entity_id) is not int or entity_id <= 0:
            raise ValueError("ID должен быть положительным целым числом.")
        self._id = entity_id
        self.name = name

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = validate_title(value)

    def __str__(self) -> str:
        return f"{self.id}. {self.name}"
