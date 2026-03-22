# Next Steps

This scaffold now defines the MVP shape, but the real implementation work is still ahead. The goal of the next phase is to replace placeholders with Claude-hook-aware, model-backed, blocking behavior while keeping control flow explicit and file-backed.

## Priority Order

1. Hook payload fidelity and mutation normalization
2. Real knowledge gate model integration
3. QA loop scoring, persistence, and user interaction hardening
4. Integration tests and end-to-end local verification

## Workstreams For Four People

### Person 1: Claude Hook + Mutation Interface

Own the Claude-facing interception path in `hooks/` and the normalization seam in `core/normalize.py`.

Scope:
- Replace scaffold payload assumptions with the real Claude Code `PreToolUse` payload shape.
- Enumerate day-one mutation tools and document exactly how each maps into `ChangeProposal`.
- Improve old/new content capture for `Write`, `Edit`, `MultiEdit`, and any other supported mutation tools.
- Add repo-local note discovery and relevant transcript extraction inputs for context aggregation.
- Confirm the emitted `allow` and `deny` contract matches Claude hook expectations.

Deliverables:
- Real payload parser in `hooks/stdin_payload.py`
- Supported mutation-tool matrix in `hooks/README.md`
- Fixture-driven tests for each supported mutation shape in `tests/test_normalize.py`
- Hook integration tests in `tests/test_pre_tool_use.py`

Definition of done:
- We can feed real or recorded Claude hook payloads into `hooks/pre_tool_use.py` and get stable, valid decisions.

### Person 2: Knowledge Gate + Model Adapter

Own the real evaluator path in `core/gate.py` and `core/llm_adapter.py`.

Scope:
- Choose the first shipping evaluator provider and model.
- Use MCP-backed docs before wiring LangChain or provider APIs.
- Replace the deterministic scaffold gate with structured-output model evaluation.
- Enforce schema validation for `GateDecision` and fail loudly on malformed model output.
- Keep the gate adapter thin so domain models remain independent from provider objects.

Deliverables:
- Real adapter implementation in `core/llm_adapter.py`
- Prompting and structured-output handling for `GateDecision`
- Retry/error policy for transient provider failures
- Mock-based tests for valid, invalid, and partial model responses in `tests/test_gate.py`

Definition of done:
- The gate returns spec-shaped `allow` or `block` decisions from a real model and degrades clearly when the provider fails.

### Person 3: QA Loop + Competence Updates

Own the blocked-path teaching loop in `qa/` and the competence update rules in `core/competence_store.py` and `qa/competence_updates.py`.

Scope:
- Replace heuristic answer evaluation with better mechanism-focused scoring.
- Improve adaptive retry behavior so follow-up questions become more scaffolded after failure.
- Persist pending/results artifacts in a shape that will stay audit-friendly.
- Tighten competence update policy for first-pass success, retry success, and fail-limit continuation.
- Decide when terminal is enough and when the optional Gradio path should be activated for `faded_example`.

Deliverables:
- Better evaluation logic in `qa/evaluation.py`
- Richer retry/question adaptation in `qa/question_generation.py`
- Finalized result artifact shape in `state/qa/results/`
- Expanded QA tests covering pass-first-try, pass-after-retry, and fail-3x behavior in `tests/test_qa_loop.py`

Definition of done:
- A blocked change can go through a full 1-3 attempt loop with consistent scoring and competence updates.

### Person 4: End-to-End Reliability + Local UX

Own integration quality, state ergonomics, and optional UI readiness.

Scope:
- Build realistic end-to-end tests that exercise hook -> gate -> QA -> state persistence.
- Improve event logging in `state/logs/events.jsonl` so runs are debuggable.
- Add local developer commands and workflow notes for replaying intercepted payloads.
- Prototype the optional Gradio flow only if terminal UX is insufficient for `faded_example` questions.
- Keep docs current as architecture assumptions become concrete.

Deliverables:
- Integration-style tests for representative allow/block flows
- Event logging helpers and log assertions
- Developer workflow documentation in `README.md` or a dedicated local-dev doc
- Optional first-pass `qa/gradio_renderer.py` implementation if needed

Definition of done:
- A teammate can locally replay a realistic flow, inspect artifacts under `state/`, and understand what happened without reading source code first.

## Cross-Cutting Agreements

- Preserve the MVP boundary: one agent, one synchronous gate, one blocking QA loop.
- Keep persisted artifacts human-readable.
- Do not introduce LangGraph or hidden orchestration state.
- Prefer small modules and explicit boundaries over convenience abstractions.
- Update `AGENTS.md` and `README.md` whenever the canonical workflow changes.

## Suggested Sequence

1. Person 1 locks down the real Claude payload and mutation normalization.
2. Person 2 wires the actual gate model once the normalized packet is stable.
3. Person 3 hardens QA evaluation and competence updates against the real gate output.
4. Person 4 stitches the flow together with replay tooling, logs, docs, and optional Gradio if terminal UX falls short.

## Handoff Points

- Person 1 -> Person 2: finalized `ChangeProposal` and aggregated context contract
- Person 2 -> Person 3: stable `GateDecision` and `QAPacket` schema from real model output
- Person 3 -> Person 4: stable QA result artifacts and competence update semantics
- Person 4 -> everyone: replay harness, integration tests, and debug workflow
