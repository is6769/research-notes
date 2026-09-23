"""Проверки хранения, миграции и защиты от повреждения данных."""

import unittest
from pathlib import Path
from unittest.mock import patch

from catalog import Notebook
from storage import StorageError, from_data, load_data, save_data, to_data
from tests.helpers import temporary_directory


class StorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = temporary_directory()
        self.path = Path(self.temp.__enter__()) / "notes.json"
        self.addCleanup(self.temp.__exit__, None, None, None)
        self.book = Notebook()
        self.book.add_researcher("Анна", "anna@example.org")
        self.book.add_category("Наблюдения")
        self.book.add_project("Опыт", 1)
        self.book.add_note("Измерение", "Первая строка\nВторая", 1, 1, 1)

    def test_round_trip_restores_object_identity(self) -> None:
        save_data(self.path, self.book)
        loaded = load_data(self.path)
        self.assertEqual(to_data(loaded), to_data(self.book))
        self.assertIs(loaded.notes[1].author, loaded.projects[1].owner)
        self.assertIs(loaded.notes[1].project, loaded.projects[1])

    def test_missing_file(self) -> None:
        self.assertFalse(load_data(self.path).notes)

    def test_corrupt_json_is_not_overwritten(self) -> None:
        self.path.write_text("{broken", encoding="utf-8")
        with self.assertRaises(StorageError):
            load_data(self.path)
        self.assertEqual(self.path.read_text(), "{broken")

    def test_broken_reference(self) -> None:
        data = to_data(self.book)
        data["notes"][0]["project_id"] = 999
        with self.assertRaises(StorageError):
            from_data(data)

    def test_duplicate_id(self) -> None:
        data = to_data(self.book)
        data["notes"].append(data["notes"][0].copy())
        with self.assertRaises(StorageError):
            from_data(data)

    def test_invalid_schema(self) -> None:
        for data in ({}, None, "text", {"version": 2}):
            with self.subTest(data=data), self.assertRaises(StorageError):
                from_data(data)

    def test_invalid_status_and_reference_types(self) -> None:
        for field, value in [("archived", "false"), ("author_id", True)]:
            data = to_data(self.book)
            data["notes"][0][field] = value
            with self.subTest(field=field), self.assertRaises(StorageError):
                from_data(data)

    def test_failed_replace_preserves_file(self) -> None:
        save_data(self.path, self.book)
        original = self.path.read_bytes()
        self.book.notes[1].edit("Изменено", "Текст")
        with patch("storage.os.replace", side_effect=OSError("disk error")):
            with self.assertRaises(StorageError):
                save_data(self.path, self.book)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertFalse(list(self.path.parent.glob("*.tmp")))

    def test_migrate_pr2_preserves_note(self) -> None:
        book = from_data([{"id": 7, "title": "Старая заметка",
                           "text": "Данные ПР2", "archived": True}])
        self.assertEqual(book.notes[7].text, "Данные ПР2")
        self.assertTrue(book.notes[7].archived)
        self.assertIs(book.notes[7].author, book.researchers[1])

    def test_duplicate_after_catalog_edit_rejected(self) -> None:
        self.book.add_category("Литература")
        self.book.categories[2].name = "наблюдения"
        with self.assertRaises(StorageError):
            save_data(self.path, self.book)
        self.assertFalse(self.path.exists())
