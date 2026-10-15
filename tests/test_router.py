import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from queue_compass.__main__ import read_json
from queue_compass.model import Router, evaluate


class RouterTests(unittest.TestCase):
    def setUp(self):
        self.rows = json.loads(Path("data/train.json").read_text())
        self.router = Router(self.rows)

    def test_route_and_normalization(self):
        result = self.router.predict("refund duplicate payment invoice")
        self.assertEqual(result["route"], "billing")
        self.assertTrue(math.isclose(sum(result["model_scores"].values()), 1))
        self.assertTrue(result["human_review_required"])
        self.assertTrue(result["evidence"])

    def test_unknown_and_repetition_abstain(self):
        for text in ["purple elephants dance", "refund " * 50, "1234 !!!!"]:
            self.assertTrue(self.router.predict(text)["abstained"])

    def test_coverage_abstains(self):
        self.assertEqual(
            self.router.predict("refund payment xyz abc zzz zzz zzz")["reason"],
            "low_vocabulary_coverage",
        )

    def test_score_abstains(self):
        self.assertEqual(
            self.router.predict("refund password", threshold=1)["reason"],
            "low_model_score",
        )

    def test_invalid_text_and_threshold(self):
        for value in ["", " ", None, 123, "a" * 10001]:
            with self.assertRaises(ValueError):
                self.router.predict(value)
        with self.assertRaises(ValueError):
            self.router.predict("refund payment", threshold=float("nan"))

    def test_invalid_training(self):
        for data in [
            [],
            {},
            self.rows + [self.rows[0]],
            [{"text": "hi", "label": "bad label"}] * 4,
            [{"text": "hi"}] * 4,
            [{"text": "!!!", "label": "a"}] * 4,
            self.rows[:8],
        ]:
            with self.assertRaises(ValueError):
                Router(data)

    def test_deterministic(self):
        self.assertEqual(
            self.router.predict("API server timeout"),
            Router(list(reversed(self.rows))).predict("API server timeout"),
        )

    def test_holdout_no_duplicate_leakage(self):
        test = json.loads(Path("data/test.json").read_text())
        self.assertFalse({r["text"].lower() for r in self.rows} & {r["text"].lower() for r in test})
        metrics = evaluate(self.router, test)
        self.assertGreaterEqual(metrics["selective_accuracy"], 0.8)
        self.assertGreaterEqual(metrics["unknown_rejection_rate"], 0.75)
        self.assertGreaterEqual(metrics["coverage"], 0.5)

    def test_empty_evaluation(self):
        for data in [[], [{"text": "hello", "label": "invalid"}]]:
            with self.assertRaises(ValueError):
                evaluate(self.router, data)
        self.assertIsNone(
            evaluate(self.router, [{"text": "xyz abc", "label": "unknown"}])["selective_accuracy"]
        )

    def test_bounded_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_bytes(b" " * 2_000_001)
            with self.assertRaises(ValueError):
                read_json(path)

    def test_cli(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "queue_compass",
                "predict",
                "--input",
                "data/ticket.json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(json.loads(result.stdout)["route"], "billing")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "queue_compass",
                "predict",
                "--input",
                "missing.json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)
