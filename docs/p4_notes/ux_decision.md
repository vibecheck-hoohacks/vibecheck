# UX Decision — Phases 5-6 Notes

## Terminal Renderer Improvements (Phase 5)
- Added `Attempt N/M` header with question type label
- Added visual separator bars (`─` × 60)
- Added type-specific intro text:
  - faded_example: "Fill in the blanks below:"
  - true_false: "Answer True or False:"
  - plain_english: (no extra intro, question speaks for itself)
- Added `show_feedback()` for inline pass/fail display
- Added `show_outcome()` for final result summary
- EOF and empty input handled gracefully (returns empty string)

## Gradio Decision (Phase 6)
**Decision: IMPLEMENT for faded_example questions.**

### Why
The faded_example question type asks users to write code. In a terminal:
- No syntax highlighting
- No line numbers
- No code editor affordances
- Can't see blanks visually distinguished from surrounding code
- Multiline input is awkward

Gradio's `gr.Code(language="python")` component provides all of the above.

### Scope compliance
Implementation touches ONLY:
- `qa/gradio_renderer.py` — full implementation
- `qa/renderer_selection.py` — passes max_attempts through

Does NOT touch:
- `core/gate.py` (Person 2 scope)
- `core/llm_adapter.py` (Person 2 scope)
- `qa/evaluation.py` (Person 3 scope)

### Architecture
- Blocking `ask()` via `threading.Thread` + `queue.Queue`
- Each question launches a fresh Gradio app, waits for submission
- 5-minute timeout safety via `queue.get(timeout=300)`
- Graceful cleanup via `app.close()`
- Falls back to terminal when gradio not installed (`gradio_available()`)

### Not yet wired
- The Gradio renderer doesn't show feedback/outcome *within* the browser UI — those still go to stderr. A future improvement could update the Gradio UI with feedback between attempts.
- No end-to-end test (requires gradio installed).
