from pathlib import Path

from catalog import Notebook
from storage import from_data, save_data

EXAMPLE_DATA = {
    "version": 1,
    "researchers": [
        {
            "id": 1,
            "name": "Анна Исследователь",
            "email": "anna@example.org"
        },
        {
            "id": 2,
            "name": "Иван Аналитик",
            "email": "ivan@example.org"
        }
    ],
    "categories": [
        {
            "id": 1,
            "name": "Наблюдения"
        },
        {
            "id": 2,
            "name": "Литература"
        }
    ],
    "projects": [
        {
            "id": 1,
            "name": "Качество воды",
            "owner_id": 1,
            "archived": False
        },
        {
            "id": 2,
            "name": "Обзор методов анализа",
            "owner_id": 2,
            "archived": False
        }
    ],
    "notes": [
        {
            "id": 1,
            "title": "Измерение температуры",
            "text": "Проба A: температура 20 °C.\nПовторить измерение утром.",
            "author_id": 1,
            "project_id": 1,
            "category_id": 1,
            "archived": False,
            "created_at": "2026-09-22T18:14:06.080587",
            "updated_at": "2026-09-22T18:14:06.080587"
        },
        {
            "id": 2,
            "title": "Методы фильтрации",
            "text": (
                "Сравнить угольные и мембранные фильтры.\n"
                "Источник: учебный обзор методов очистки."
            ),
            "author_id": 2,
            "project_id": 2,
            "category_id": 2,
            "archived": False,
            "created_at": "2026-09-22T18:14:06.080656",
            "updated_at": "2026-09-22T18:14:06.080656"
        },
        {
            "id": 3,
            "title": "Пилотное наблюдение",
            "text": "Завершённый предварительный опыт.",
            "author_id": 1,
            "project_id": 1,
            "category_id": 1,
            "archived": True,
            "created_at": "2026-09-22T18:14:06.080669",
            "updated_at": "2026-09-22T18:14:06.080676"
        }
    ]
}


def create_demo() -> Notebook:
    return from_data(EXAMPLE_DATA)


if __name__ == "__main__":
    path = Path(__file__).resolve().parents[1] / "data/example.json"
    save_data(path, create_demo())
