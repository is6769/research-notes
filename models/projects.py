from __future__ import annotations

from utils import get_note_status

from .base import NamedEntity
from .researchers import Researcher


class Project(NamedEntity):
    """Исследовательский проект с владельцем и архивным состоянием."""

    def __init__(
        self, entity_id: int, name: str, owner: Researcher,
        archived: bool = False,
    ) -> None:
        super().__init__(entity_id, name)
        if not isinstance(owner, Researcher):
            raise ValueError("Владелец должен быть исследователем.")
        if type(archived) is not bool:
            raise ValueError("Состояние архива должно быть логическим.")
        self.owner = owner
        self._archived = archived

    @property
    def archived(self) -> bool:
        return self._archived

    def archive(self) -> None:
        self._archived = True

    def restore(self) -> None:
        self._archived = False

    def __str__(self) -> str:
        return (f"{super().__str__()} | {self.owner.name} | "
                f"{get_note_status(self.archived)}")
