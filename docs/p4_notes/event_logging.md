# Event Logging — Phase 1 Notes

## What was built
- `core/event_logger.py`: Append-only JSONL `EventLogger` class
- Instrumented `hooks/pre_tool_use.py` with 6 lifecycle events
- Instrumented `qa/loop.py` with 3 QA lifecycle events

## Event sequence (blocked flow)
```
hook_payload_received → mutation_normalized → context_aggregated →
gate_decision_made → qa_attempt_started → qa_answer_evaluated →
competence_updated → decision_returned
```

## Event sequence (allow flow)
```
hook_payload_received → mutation_normalized → context_aggregated →
gate_decision_made → decision_returned
```

## Event sequence (bypass flow)
```
hook_payload_received → non_mutation_bypass
```

## Design decisions
- Logger is injected via parameter, not global state
- QALoop uses optional `_log()` wrapper to avoid breaking existing callers
- Events use compact JSON (`separators=(",",":")`) for smaller log files
- `read_events()` method added for test convenience
