"""Проверки настоящего консольного процесса на временных данных."""

import os
import subprocess
import sys
import unittest
from pathlib import Path

from storage import load_data
from tests.helpers import temporary_directory

ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def run_cli(
        self, path: Path, commands: str,
    ) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(ROOT / "main.py"), "--data", str(path)],
            input=commands, text=True, encoding="utf-8", capture_output=True,
            timeout=15, env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )

    def test_create_and_reopen(self) -> None:
        with temporary_directory() as directory:
            path = Path(directory) / "notes.json"
            commands = (
                "8\n1\n1\nАнна\nanna@example.org\n"
                "8\n2\n1\nПроект\n1\n"
                "8\n3\n1\nКатегория\n"
                "2\n1\n1\n1\nЗаметка\nСтрока 1\nСтрока 2\n.\n0\n"
            )
            result = self.run_cli(path, commands)
            self.assertEqual(result.returncode, 0, result.stderr)
            book = load_data(path)
            self.assertEqual(book.notes[1].text, "Строка 1\nСтрока 2")
            result = self.run_cli(path, "4\n1\n0\n")
            self.assertIn("Строка 2", result.stdout)

    def test_invalid_input_recovers(self) -> None:
        with temporary_directory() as directory:
            result = self.run_cli(Path(directory) / "notes.json", "x\n1\n0")
            self.assertEqual(result.returncode, 0)
            self.assertIn("Нет такого пункта", result.stdout)

    def test_corrupt_file_fails_without_traceback(self) -> None:
        with temporary_directory() as directory:
            path = Path(directory) / "notes.json"
            path.write_text("{invalid", encoding="utf-8")
            result = self.run_cli(path, "0\n")
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(path.read_text(), "{invalid")

    def test_eof_discards_incomplete_command(self) -> None:
        with temporary_directory() as directory:
            path = Path(directory) / "notes.json"
            result = self.run_cli(path, "8\n1\n1\nАнна\n")
            self.assertEqual(result.returncode, 0)
            self.assertFalse(path.exists())
