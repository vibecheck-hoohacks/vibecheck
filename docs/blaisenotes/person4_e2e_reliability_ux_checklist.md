# Person 4 Near-Term Checklist

This document scopes the most useful near-term work for Person 4: end-to-end reliability and local UX.

The goal is not to finish the full product before the other workstreams land. The goal is to make the current scaffold replayable, debuggable, and easy for teammates to validate locally.

## Current Constraint

Person 4 should optimize for the current scaffolded flow:

- hook entry
- mutation normalization
- gate decision
- QA loop
- persisted state artifacts

Do not block on:

- final Claude Code payload fidelity
- real model-backed gate behavior
- final QA scoring semantics
- packaging or distribution work unless demo setup becomes a real bottleneck

## Near-Term Outcome

Definition of a good near-term result:

- a teammate can run a small set of local replay scenarios
- the run produces readable artifacts under `state/`
- the run produces structured event logs for debugging
- representative allow and block flows are covered by tests
- terminal UX is understandable enough for a live demo

## Priority 1: Replayable End-to-End Flows

### Goal

Make the current scaffold easy to exercise repeatedly without depending on unfinished upstream work.

### Deliverables

- A small fixture set for representative hook payloads
- A documented local replay command or script entrypoint
- Integration-style tests that drive `hooks/pre_tool_use.py`

### Checklist

- [ ] Define 3 to 5 representative replay scenarios
- [ ] Add payload fixtures for an allow path
- [ ] Add payload fixtures for a block-then-pass path
- [ ] Add payload fixtures for a block-then-fail-limit path
- [ ] Add at least one malformed payload fixture
- [ ] Make replay output easy to inspect in `state/`
- [ ] Document expected artifacts produced by each scenario

### Suggested Scenario Set

1. Small single-file `Write` change that should allow immediately
2. Larger or multi-file change that should block and then pass on attempt 2
3. Blocked change that fails all 3 attempts and still resolves to `allow`
4. Invalid payload that returns a clean deny response
5. Non-mutation tool that bypasses VibeCheck cleanly

## Priority 2: Event Logging

### Goal

Make each run debuggable without stepping through source code.

### Deliverables

- A small event logging helper
- Lifecycle events written to `state/logs/events.jsonl`
- Tests that assert key events are emitted in order

### Checklist

- [ ] Define a minimal event schema before writing code
- [ ] Log hook payload receipt
- [ ] Log mutation normalization success or failure
- [ ] Log context aggregation completion
- [ ] Log gate decision with proposal id and decision type
- [ ] Log each QA attempt with attempt number and pass/fail
- [ ] Log competence update outcome
- [ ] Log final allow/deny response
- [ ] Keep events machine-friendly and human-inspectable

### Minimum Event Fields

- `timestamp`
- `event`
- `proposal_id`
- `session_id`
- `tool_name`
- `status`
- `details`

## Priority 3: Terminal UX Hardening

### Goal

Make the blocking QA path understandable and resilient enough for local demos.

### Deliverables

- Clearer terminal prompts
- Better retry messaging
- Defined behavior for non-interactive or empty-input cases

### Checklist

- [ ] Show attempt count in every prompt
- [ ] Clearly distinguish question, answer, feedback, and outcome
- [ ] Handle empty input explicitly
- [ ] Handle EOF or missing TTY gracefully
- [ ] Ensure follow-up prompts are more scaffolded after failure
- [ ] Make final outcome wording match persisted result artifacts
- [ ] Verify terminal wording is concise enough for repeated use

### Demo Standard

If a teammate sees a blocked flow once, they should be able to answer these questions without opening the source:

- Why was the change blocked?
- What am I being asked to explain?
- Which attempt am I on?
- What happened after my answer?
- Where can I inspect the result?

## Priority 4: Reliability Tests Around Failure Modes

### Goal

Raise confidence in the seams most likely to fail during local demos.

### Deliverables

- Expanded integration and seam tests
- Assertions over artifacts and logs, not just return values

### Checklist

- [ ] Test malformed JSON payload handling
- [ ] Test empty payload handling
- [ ] Test blocked gate decision without `qa_packet`
- [ ] Test missing or malformed competence model state
- [ ] Test QA fail-limit path artifact creation
- [ ] Test terminal renderer edge cases
- [ ] Test event log creation on both success and failure paths
- [ ] Test that non-mutation tools bypass cleanly without QA artifacts

## Priority 5: Local Developer Workflow Docs

### Goal

Make it easy for anyone on the team to run and inspect a realistic local flow.

### Deliverables

- README updates or a dedicated local-dev doc
- A short replay workflow
- An artifact inspection guide

### Checklist

- [ ] Document setup with `uv sync`
- [ ] Document how to run the replay scenarios
- [ ] Document where state artifacts appear
- [ ] Document how to reset local state between runs
- [ ] Document what a normal allow flow looks like
- [ ] Document what a normal blocked flow looks like
- [ ] Document current scaffold limitations so expectations stay realistic

## Backburner: Packaging / Distribution

Keep this out of the critical path for now.

Revisit only if one of these becomes true:

- teammates are struggling to run the demo locally
- judges or external testers need a simpler install path
- replay tooling becomes polished enough that packaging improves adoption

If revisited later, possible directions are:

- a console script entrypoint for local replay
- a lightweight installable package for the hook and replay tools
- a demo-focused package command rather than a full distribution strategy

## Recommended Execution Order

1. Define replay scenarios and fixture shapes
2. Add integration-style tests around those scenarios
3. Add lifecycle event logging
4. Harden terminal UX around blocked flows
5. Write local replay and artifact inspection docs
6. Re-evaluate whether Gradio or packaging is still necessary

## Done For Now

Person 4 near-term work is successful when:

- local replay is easy
- failures are inspectable
- tests cover representative flows
- terminal QA is demo-safe
- docs make the scaffold understandable to a new teammate
