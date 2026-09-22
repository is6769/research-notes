"""ПР1: подготовка одной исследовательской заметки."""

from datetime import date
from math import ceil


def validate_title(title: str) -> str:
    """Проверить название заметки."""
    title = title.strip()
    if not title:
        raise ValueError("Название не должно быть пустым.")
    return title


def reading_minutes(word_count: int) -> int:
    """Оценить время чтения при скорости 200 слов в минуту."""
    if word_count < 0:
        raise ValueError("Количество слов не может быть отрицательным.")
    return max(1, ceil(word_count / 200))


def get_note_status(is_archived: bool) -> str:
    """Получить понятное пользователю состояние заметки."""
    if is_archived:
        return "В архиве"
    return "Активна"


def main() -> None:
    """Проверить название, оценить чтение и вывести статус."""
    try:
        title = validate_title(input("Название заметки: "))
        words = int(input("Количество слов: "))
        minutes = reading_minutes(words)
        print(f"{title} | {date.today()} | {minutes} мин.")
        print(get_note_status(False))
    except ValueError as error:
        print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
