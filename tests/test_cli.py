import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from sql_playground.cli import main


class CliTests(unittest.TestCase):
    def test_end_to_end_exec_query_and_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / "demo.db"
            script = root / "setup.sql"
            script.write_text("CREATE TABLE t(id INTEGER, label TEXT); INSERT INTO t VALUES(1, 'one');", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(db), "exec", str(script)]), 0)
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main([str(db), "query", "SELECT * FROM t", "--format", "json"]), 0)
            self.assertEqual(json.loads(output.getvalue()), [{"id": 1, "label": "one"}])
            csv_path = root / "out.csv"
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(db), "export", "SELECT * FROM t", str(csv_path)]), 0)
            self.assertTrue(csv_path.exists())

    def test_invalid_parameter_is_clean_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            err = io.StringIO()
            with redirect_stderr(err):
                code = main([str(Path(tmp) / "x.db"), "query", "SELECT 1", "--param", "bad"])
            self.assertEqual(code, 2)
            self.assertIn("name=value", err.getvalue())


if __name__ == "__main__":
    unittest.main()
