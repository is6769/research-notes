"""Сценарии ПР2, адаптированные к объектам ПР3, и правила связей."""

import unittest

from catalog import Notebook
from notes import add_note, archive_note, find_notes
from utils import reading_minutes


class NoteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.book = Notebook()
        self.author = self.book.add_researcher("Анна", "anna@example.org")
        self.category = self.book.add_category("Наблюдения")
        self.project = self.book.add_project("Опыт", self.author.id)

    def create(self, title: str = "Наблюдение", text: str = "Текст"):
        return add_note(self.book, title, text, self.author.id,
                        self.project.id, self.category.id)

    def test_add_note(self) -> None:
        note = self.create(" Наблюдение ")
        self.assertEqual(note.title, "Наблюдение")
        self.assertIs(note.author, self.author)
        self.assertIs(note.project, self.project)
        self.assertIs(note.category, self.category)

    def test_empty_title(self) -> None:
        with self.assertRaises(ValueError):
            self.create(" ")
        self.assertFalse(self.book.notes)

    def test_search(self) -> None:
        note = self.create(text="Температура 20 градусов")
        self.assertEqual(find_notes(self.book.notes.values(), "ТЕМПЕРАТУРА"),
                         [note])

    def test_archive(self) -> None:
        note = self.create()
        archive_note(self.book, note.id)
        self.assertTrue(note.archived)

    def test_reading_time_boundary(self) -> None:
        self.assertEqual(reading_minutes(201), 2)

    def test_edit_and_restore(self) -> None:
        note = self.create()
        note.edit("Результат", "Новый текст")
        self.assertEqual(note.text, "Новый текст")
        note.archive()
        with self.assertRaises(ValueError):
            note.edit("Нельзя", "Архив")
        note.restore()
        note.edit("Можно", "Восстановлено")
        self.assertFalse(note.archived)

    def test_invalid_edit_does_not_partially_update(self) -> None:
        note = self.create()
        with self.assertRaises(ValueError):
            note.edit("Новое название", " ")
        self.assertEqual(note.title, "Наблюдение")

    def test_project_archive_blocks_creation(self) -> None:
        self.project.archive()
        with self.assertRaises(ValueError):
            self.create()
        self.project.restore()
        self.assertIsNotNone(self.create())

    def test_project_archive_blocks_note_restore(self) -> None:
        note = self.create()
        note.archive()
        self.project.archive()
        with self.assertRaises(ValueError):
            note.restore()

    def test_unknown_relation(self) -> None:
        with self.assertRaises(ValueError):
            self.book.add_note("Опыт", "Текст", 999, 1, 1)
        self.assertFalse(self.book.notes)

    def test_delete_referenced_category(self) -> None:
        note = self.create()
        with self.assertRaises(ValueError):
            self.book.delete("categories", self.category.id)
        self.book.delete("notes", note.id)
        self.book.delete("categories", self.category.id)
        self.assertFalse(self.book.categories)

    def test_cannot_delete_project_owner(self) -> None:
        with self.assertRaises(ValueError):
            self.book.delete("researchers", self.author.id)

    def test_duplicate_email(self) -> None:
        with self.assertRaises(ValueError):
            self.book.add_researcher("Другая Анна", "ANNA@example.org")

    def test_duplicate_category(self) -> None:
        with self.assertRaises(ValueError):
            self.book.add_category(" наблюдения ")

    def test_combined_filters_and_sort(self) -> None:
        first = self.create("Бета")
        second = self.create("Альфа")
        first.archive()
        result = find_notes(self.book.notes.values(), project_id=1,
                            category_id=1, author_id=1, archived=False)
        self.assertEqual(result, [second])
        self.assertEqual(find_notes(self.book.notes.values()),
                         [second, first])

    def test_status_is_read_only(self) -> None:
        note = self.create()
        with self.assertRaises(AttributeError):
            note.archived = True
