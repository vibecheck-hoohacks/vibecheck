# State

`state/` contains inspectable file-backed artifacts for the MVP.

- `competence_model.yaml` stores the current local competence profile.
- `agg/current_attempt.md` stores the latest aggregated context packet.
- `qa/pending/` stores per-proposal QA packets waiting to resolve.
- `qa/results/` stores per-proposal QA outcomes.
- `logs/events.jsonl` stores machine-friendly event records.

These files are meant to stay human-readable and easy to diff during debugging.
