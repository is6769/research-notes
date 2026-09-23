"""Общие проверки и функции, сохранённые из ПР1."""

from math import ceil


def validate_title(title: str) -> str:
    """Вернуть непустую строку без внешних пробелов."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Текст не должен быть пустым.")
    return title.strip()


def reading_minutes(word_count: int) -> int:
    """Оценить время чтения при скорости 200 слов в минуту."""
    if type(word_count) is not int or word_count < 0:
        raise ValueError("Количество слов: целое неотрицательное число.")
    return max(1, ceil(word_count / 200))


def get_note_status(is_archived: bool) -> str:
    """Получить название состояния заметки."""
    return "В архиве" if is_archived else "Активна"


def input_int(prompt: str) -> int:
    """Прочитать положительный идентификатор."""
    value = int(input(prompt))
    if value <= 0:
        raise ValueError("Введите положительное целое число.")
    return value
