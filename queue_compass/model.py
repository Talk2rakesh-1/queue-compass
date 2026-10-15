"""Laplace-smoothed multinomial Naive Bayes with explicit abstention."""

import math
import re
from collections import Counter, defaultdict

MAX_TEXT = 10000


def tokens(text):
    if not isinstance(text, str) or not text.strip() or len(text) > MAX_TEXT:
        raise ValueError("text must contain 1–10000 characters")
    return re.findall(r"[a-z]{2,}", text.lower())


class Router:
    def __init__(self, rows):
        if not isinstance(rows, list) or not 4 <= len(rows) <= 10000:
            raise ValueError("training data must contain 4–10000 rows")
        self.counts = defaultdict(Counter)
        self.documents = Counter()
        seen = set()
        for row in rows:
            if not isinstance(row, dict) or set(row) != {"text", "label"}:
                raise ValueError("each row requires only text and label")
            label = row["label"]
            if not isinstance(label, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,39}", label):
                raise ValueError("invalid label")
            words = tokens(row["text"])
            key = tuple(words)
            if not words or key in seen:
                raise ValueError("empty token sequence or duplicate training text")
            seen.add(key)
            self.counts[label].update(words)
            self.documents[label] += 1
        if len(self.documents) < 2 or min(self.documents.values()) < 2:
            raise ValueError("need at least two classes with two examples each")
        self.vocabulary = set().union(*(set(c) for c in self.counts.values()))
        self.totals = {label: sum(c.values()) for label, c in self.counts.items()}
        self.size = sum(self.documents.values())

    def weight(self, label, word):
        return math.log(
            (self.counts[label][word] + 1) / (self.totals[label] + len(self.vocabulary))
        )

    def predict(self, text, threshold=0.80, minimum_coverage=0.5):
        if not 0 <= threshold <= 1 or not 0 <= minimum_coverage <= 1:
            raise ValueError("thresholds must be between zero and one")
        words = tokens(text)
        known = Counter(w for w in words if w in self.vocabulary)
        coverage = sum(known.values()) / max(1, len(words))
        scores = {
            label: math.log(n / self.size)
            + sum(count * self.weight(label, word) for word, count in known.items())
            for label, n in sorted(self.documents.items())
        }
        top = max(scores.values())
        denominator = sum(math.exp(s - top) for s in scores.values())
        probabilities = {label: math.exp(s - top) / denominator for label, s in scores.items()}
        ranking = sorted(probabilities, key=lambda label: (-probabilities[label], label))
        winner, runner = ranking[:2]
        reason = None
        if sum(known.values()) < 2 or len(known) < 2:
            reason = "insufficient_known_words"
        elif coverage < minimum_coverage:
            reason = "low_vocabulary_coverage"
        elif probabilities[winner] < threshold:
            reason = "low_model_score"
        evidence = sorted(
            (
                {
                    "word": w,
                    "log_odds_contribution": round(
                        c * (self.weight(winner, w) - self.weight(runner, w)), 4
                    ),
                }
                for w, c in known.items()
            ),
            key=lambda e: (-abs(e["log_odds_contribution"]), e["word"]),
        )[:8]
        return {
            "route": None if reason else winner,
            "candidate": winner,
            "abstained": reason is not None,
            "reason": reason,
            "model_scores": probabilities,
            "vocabulary_coverage": coverage,
            "evidence_against": runner,
            "evidence": evidence,
            "human_review_required": True,
        }


def evaluate(router, rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError("evaluation rows must be a nonempty list")
    accepted = correct = unknown_rejected = unknown_total = 0
    confusion = defaultdict(Counter)
    for row in rows:
        if set(row) != {"text", "label"} or row["label"] not in {
            *router.documents,
            "unknown",
        }:
            raise ValueError("invalid evaluation label or schema")
        result = router.predict(row["text"])
        route = result["route"] or "abstain"
        confusion[row["label"]][route] += 1
        accepted += not result["abstained"]
        correct += result["route"] == row["label"]
        unknown_total += row["label"] == "unknown"
        unknown_rejected += row["label"] == "unknown" and result["abstained"]
    return {
        "examples": len(rows),
        "accepted": accepted,
        "correctly_routed": correct,
        "coverage": accepted / len(rows),
        "selective_accuracy": correct / accepted if accepted else None,
        "unknown_rejection_rate": unknown_rejected / unknown_total if unknown_total else None,
        "confusion": dict(confusion),
    }
