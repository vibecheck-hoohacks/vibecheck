# Test Coverage — Phases 2-4 Notes

## Starting state
- 28 tests across 6 test files

## Ending state
- 89 tests across 15 test files (+61 tests, +9 files)

## New test files
- `tests/test_replay_fixtures.py` — 13 fixture-driven integration tests
- `tests/test_failure_modes.py` — 10 edge-case tests
- `tests/test_terminal_renderer.py` — 8 renderer UX tests
- `tests/test_cli.py` — CLI command smoke tests
- `tests/test_cc_init.py` — Claude Code hook bootstrap coverage
- `tests/test_config.py` — auth/config persistence coverage
- `tests/test_concept_resolver.py` — taxonomy lookup coverage
- `tests/test_concept_taxonomy.py` — concept graph loading coverage
- `tests/test_openrouter_client.py` — OpenRouter client behavior coverage

## Enhanced existing tests
- `tests/test_pre_tool_use.py` — added artifact structure assertions and event log verification to bypass, allow, and blocked flow tests
- `tests/test_gate.py` — now covers the live gate path with injectable client behavior
- `tests/test_qa_loop.py` — expanded alongside the LLM-integrated QA loop path

## Coverage gaps remaining
- No tests for Gradio renderer (can't test without gradio installed)
- No tests for concurrent/parallel hook invocations
- No property-based testing for normalizer edge cases
- No tests for transcript extraction edge cases (large files, malformed JSON)

## Fixtures
5 replay fixtures in `tests/fixtures/`:
1. Small write → allow
2. Large write → block → pass
3. Large write → block → fail limit
4. Malformed payload → error
5. Non-mutation → bypass
