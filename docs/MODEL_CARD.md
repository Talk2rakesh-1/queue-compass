# Model card

- **Task:** English support-ticket queue suggestion, single-label classification.
- **Model:** multinomial Naive Bayes, additive smoothing alpha=1, empirical class priors; fit at invocation.
- **Features:** lowercase ASCII alphabetic tokens of length at least two; counts; no stemming, embeddings, or stop-word removal.
- **Training data:** 24 original synthetic messages, eight per class; MIT. No external datasets or weights.
- **Evaluation:** 16 separately written synthetic messages. This is regression data, not representative sampling. Test vocabulary intentionally overlaps training vocabulary. No hyperparameter search was performed; thresholds are heuristic.
- **Abstention:** fewer than two distinct known words, known-token fraction below 0.5, or highest model score below 0.8. No claimed OOD detection guarantee.
- **Explainability:** token count × difference between winning and runner-up log likelihood. Priors also influence the decision and are not included in word evidence.
- **Failure modes:** negation, mixed topics, multilingual input, label imbalance, drift, novel phrasing, and repeated/inserted keywords. Unknown terms are discarded for scoring but count against coverage.
- **Excluded uses:** autonomous incident suppression, severity assignment, employment, credit, medical, legal, or other consequential decisions.
- **Privacy:** no network or telemetry. Outputs can expose input words. Keep sensitive tickets and model training data out of Git.
- **Operational path:** evaluate a representative temporal holdout and human disagreement, calibrate, compare with a majority baseline and stronger models, monitor per-class false routing, and deploy with human review only.
