# QueueCompass

[![CI](https://github.com/Talk2rakesh-1/queue-compass/actions/workflows/ci.yml/badge.svg)](https://github.com/Talk2rakesh-1/queue-compass/actions/workflows/ci.yml)
[![Security](https://github.com/Talk2rakesh-1/queue-compass/actions/workflows/security.yml/badge.svg)](https://github.com/Talk2rakesh-1/queue-compass/actions/workflows/security.yml)

An inspectable, local machine-learning CLI for **human-reviewed support-ticket routing**. It learns word frequencies from labeled examples, proposes billing/access/reliability queues, and abstains when the evidence is weak. No API key, paid service, model download, or runtime dependency.

**Status:** functional portfolio MVP, not a validated production routing model. The included data is deliberately small and synthetic.

## Try it

Use Python 3.10+ (also locally checked on Python 3.9). From this repository:

```sh
python3 -m queue_compass validate
python3 -m queue_compass predict --input data/ticket.json
python3 -m queue_compass evaluate --input data/test.json
python3 -m unittest discover -s tests -v
```

Prediction input is a JSON object such as `{"text":"Please refund the duplicate subscription payment"}`. Output includes `route`, `candidate`, `abstained`, `reason`, per-class `model_scores`, vocabulary coverage, word evidence against the runner-up class, and `human_review_required: true`. An abstention returns `route: null`; the candidate is diagnostic only.

To use your own labeled training array, pass `--training path/to/train.json`. Rows must have exactly `text` and `label`; at least two classes with two distinct examples per class are required. Model fitting happens in memory on each run. No executable serialized artifacts are loaded. This design is intentionally suited to small routing experiments, not high-throughput serving.

## How it works

`JSON → validation → lowercase word counts → Laplace-smoothed multinomial Naive Bayes → abstention gate → JSON suggestion`

The model learns class priors and token likelihoods from training examples. Log-space scoring avoids underflow. Explanations show each known word's log-likelihood contribution relative to the runner-up. They explain the model calculation, not causation or business truth. Word order and negation are not understood. Ties are deterministic.

Defaults require two distinct known words, at least 50% known-token coverage, and a top model score of 0.80. Scores are **not calibrated confidence probabilities**. These heuristic thresholds need validation on representative data. Every result requires human review.

## Evaluation and limits

The original fixture contains 24 training examples across three classes, plus 16 separate evaluation examples (12 in-domain and four unknown). There are no identical training/evaluation texts. Shared vocabulary and authoring style make this an easy smoke test, not an unbiased benchmark.

On the included holdout: 12/16 accepted (75% coverage), 12/12 accepted routes correct (100% selective accuracy), 4/4 unknown examples rejected. Reproduce with the command above. These results do not establish real-world accuracy, calibration, fairness, incident-detection ability, or cost savings. No customer data was used.

Before operational use: collect consented examples, split by customer/time to avoid leakage, evaluate per-class recall and harmful misroutes, calibrate thresholds, test language and adversarial drift, and retain human override. This tool does not infer urgency and must not suppress incidents.

## Development

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
ruff check .
ruff format --check .
coverage run -m unittest discover -s tests -v
coverage report
bandit -r queue_compass -ll
pip-audit -r requirements.txt
python scripts/check_policy.py
```

CI runs on Python 3.10 and 3.13. Tests cover malformed data, size limits, deterministic routing, unknown input, abstention, CLI failures, and holdout regression gates. Full-history secret scanning is a separate workflow. See [security](SECURITY.md), [model card](docs/MODEL_CARD.md), [research](docs/RESEARCH.md), and [licensing](THIRD_PARTY.md).

MIT licensed. A small classical ML implementation chosen for inspectability; no generative-AI claims.
