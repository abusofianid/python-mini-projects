"""Tests for the task tracker. Run them from this folder with:  python -m unittest -v

The tests use temporary files only, so they never touch your real task.json.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import config
import manager
import storage

HERE = Path(__file__).parent


class TempStorageTestCase(unittest.TestCase):
    """Point storage.file_name at a fresh temporary file for every test."""

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "task.json"

        patcher = mock.patch.object(storage, "file_name", str(self.path))
        patcher.start()
        self.addCleanup(patcher.stop)


class LoadDataTests(TempStorageTestCase):
    def test_missing_file_gives_empty_list(self):
        self.assertEqual(storage.load_data(), [])

    def test_empty_file_gives_empty_list(self):
        self.path.write_text("")
        self.assertEqual(storage.load_data(), [])

    def test_whitespace_only_file_gives_empty_list(self):
        self.path.write_text("  \n\n")
        self.assertEqual(storage.load_data(), [])

    def test_invalid_json_gives_empty_list(self):
        self.path.write_text("{not valid json")
        self.assertEqual(storage.load_data(), [])

    def test_truncated_json_gives_empty_list(self):
        # What a half-written file looks like after a crash.
        self.path.write_text('[{"id": 1, "description": "Buy mi')
        self.assertEqual(storage.load_data(), [])

    def test_file_that_is_not_text_gives_empty_list(self):
        self.path.write_bytes(b"\xff\xfe\x00\x80 not utf-8")
        self.assertEqual(storage.load_data(), [])

    def test_json_that_is_not_a_list_gives_empty_list(self):
        # Valid JSON, but the app always saves a list, so this file is damaged.
        for text in ("{}", '{"id": 1}', "null", "5", '"text"', "true"):
            with self.subTest(text=text):
                self.path.write_text(text)
                self.assertEqual(storage.load_data(), [])

    def test_path_that_cannot_be_read_gives_empty_list(self):
        # A folder with the same name as the data file: open() fails with an OSError.
        self.path.mkdir()
        self.assertEqual(storage.load_data(), [])

    def test_valid_file_is_loaded(self):
        tasks = [{"id": 1, "description": "Buy milk", "status": "todo"}]
        self.path.write_text(json.dumps(tasks))
        self.assertEqual(storage.load_data(), tasks)

    def test_save_then_load_round_trip(self):
        tasks = [{"id": 7, "description": "Café ☕", "status": "done"}]
        storage.save_data(tasks)
        self.assertEqual(storage.load_data(), tasks)


class RecoveryTests(TempStorageTestCase):
    """The app must keep working after it meets a damaged data file."""

    def test_adding_a_task_after_a_corrupt_file_works(self):
        self.path.write_text("{not valid json")
        tasks = manager.taskmanager()

        new_id = tasks.add_task("First task")

        self.assertEqual(new_id, 1)
        self.assertEqual([t["description"] for t in tasks.list_tasks()], ["First task"])
        # The damaged file was replaced by a valid one.
        self.assertEqual(json.loads(self.path.read_text())[0]["id"], 1)

    def test_listing_after_a_corrupt_file_shows_no_tasks(self):
        self.path.write_text("[[[")
        self.assertEqual(manager.taskmanager().list_tasks(), [])
        self.assertEqual(manager.taskmanager().list_tasks(config.status_done), [])


class ManagerTests(TempStorageTestCase):
    def test_ids_increase_and_statuses_change(self):
        tasks = manager.taskmanager()
        first = tasks.add_task("one")
        second = tasks.add_task("two")

        self.assertEqual((first, second), (1, 2))
        self.assertTrue(tasks.update_task_status(2, config.status_done))
        self.assertEqual(
            [t["id"] for t in tasks.list_tasks(config.status_done)],
            [2],
        )
        self.assertFalse(tasks.update_task_status(99, config.status_done))

    def test_delete_and_update(self):
        tasks = manager.taskmanager()
        tasks.add_task("one")
        tasks.add_task("two")

        self.assertTrue(tasks.update_task(1, "uno"))
        self.assertFalse(tasks.update_task(99, "x"))
        self.assertTrue(tasks.delete_task(1))
        self.assertFalse(tasks.delete_task(1))
        self.assertEqual([t["description"] for t in tasks.list_tasks()], ["two"])


class HelpTextTests(unittest.TestCase):
    """The help text must name the status values the program really accepts."""

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        # Run a copy of the program, so the real task.json is never read or written.
        for source in HERE.glob("*.py"):
            if not source.name.startswith("test_"):
                shutil.copy2(source, folder.name)
        self.folder = folder.name

    def run_cli(self, text):
        return subprocess.run(
            [sys.executable, str(Path(self.folder, "main.py"))],
            input=text,
            capture_output=True,
            text=True,
            env={**os.environ, "TERM": "dumb"},
            cwd=self.folder,
            timeout=30,
            check=False,
        ).stdout

    def test_help_lists_the_real_status_values(self):
        output = self.run_cli("help\nexit\n")

        list_line = next(
            line for line in output.splitlines() if "list [status]" in line
        )
        for status in (
            config.status_todo,
            config.status_in_progress,
            config.status_done,
        ):
            self.assertIn(status, list_line)

    def test_every_status_named_in_help_is_accepted_as_a_filter(self):
        statuses = (config.status_todo, config.status_in_progress, config.status_done)
        commands = "".join(f"list {status}\n" for status in statuses) + "exit\n"

        output = self.run_cli(commands)

        self.assertNotIn("Invalid status filter", output)


if __name__ == "__main__":
    unittest.main()
