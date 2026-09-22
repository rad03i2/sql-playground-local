import csv
import tempfile
import unittest
from pathlib import Path

from sql_playground.core import Playground, PlaygroundError


class PlaygroundTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "test.db"
        self.db = Playground(self.path)
        self.db.execute_script("CREATE TABLE items(id INTEGER PRIMARY KEY, name TEXT NOT NULL, score INTEGER); INSERT INTO items(name, score) VALUES ('A', 5), ('B', 9);")

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def test_query_with_named_parameter(self):
        result = self.db.query("SELECT name FROM items WHERE score >= :min ORDER BY name", {"min": 6})
        self.assertEqual(result.columns, ("name",))
        self.assertEqual(result.rows, (("B",),))

    def test_mutation_rejected_in_query(self):
        with self.assertRaises(PlaygroundError):
            self.db.query("DELETE FROM items")
        self.assertEqual(self.db.query("SELECT count(*) AS n FROM items").rows[0][0], 2)

    def test_multiple_statements_rejected_by_sqlite_execute(self):
        with self.assertRaises(PlaygroundError):
            self.db.query("SELECT 1; SELECT 2")

    def test_failed_script_rolls_back(self):
        with self.assertRaises(PlaygroundError):
            self.db.execute_script("INSERT INTO items(name) VALUES ('C'); INSERT INTO missing VALUES (1);")
        self.assertEqual(self.db.query("SELECT count(*) FROM items").rows[0][0], 2)

    def test_schema_and_describe(self):
        names = {row[1] for row in self.db.schema().rows}
        self.assertIn("items", names)
        columns = {row[1] for row in self.db.describe("items").rows}
        self.assertEqual(columns, {"id", "name", "score"})
        with self.assertRaises(PlaygroundError):
            self.db.describe("missing")

    def test_csv_export(self):
        out = Path(self.temp.name) / "nested" / "items.csv"
        count = self.db.export_csv("SELECT name, score FROM items ORDER BY id", out)
        self.assertEqual(count, 2)
        with out.open(encoding="utf-8", newline="") as handle:
            self.assertEqual(list(csv.reader(handle)), [["name", "score"], ["A", "5"], ["B", "9"]])


if __name__ == "__main__":
    unittest.main()
