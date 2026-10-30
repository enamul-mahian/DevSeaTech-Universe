"""Regression checks for crash recovery bootstrap ordering.

The constructor starts an autosave, so recovery must be loaded before it.
These checks run without Qt and complement the GUI smoke test.
"""
import ast
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src" / "devseatech_browser" / "app.py"


class CrashRecoveryBootstrapTests(unittest.TestCase):
    def test_restore_is_read_before_browser_constructor(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        main = next(node for node in tree.body
                    if isinstance(node, ast.FunctionDef) and node.name == "main")
        assignments = [
            (index, node.value)
            for index, node in enumerate(main.body)
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call)
        ]
        restore = [
            index for index, call in assignments
            if isinstance(call.func, ast.Attribute)
            and call.func.attr == "restore_tabs_from"
        ]
        browser = [
            index for index, call in assignments
            if isinstance(call.func, ast.Name)
            and call.func.id == "Browser"
        ]
        self.assertEqual(len(restore), 1)
        self.assertEqual(len(browser), 1)
        self.assertLess(restore[0], browser[0],
                        "Browser constructor autosaves and may destroy prior recovery data")

    def test_recovery_is_saved_after_selection(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        main = next(node for node in tree.body
                    if isinstance(node, ast.FunctionDef) and node.name == "main")
        calls = [
            node for node in ast.walk(main)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "_auto_save_session"
        ]
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
