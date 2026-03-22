# QA Loop

`qa/` holds the blocking knowledge-check path that runs after the gate returns `block`.

- `loop.py` manages attempts, persistence, and competence updates.
- `terminal_renderer.py` is the day-one interaction path.
- `gradio_renderer.py` marks the optional Python web UI seam for richer question types.

The current scaffold keeps the Gradio boundary explicit but unimplemented so the terminal flow remains the default until browser UX is necessary.
