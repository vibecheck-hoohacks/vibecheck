Yes — here is a **diagram-faithful Claude Code–only MVP spec** centered on **intercepting `Write` before it lands**.

The crucial Claude Code fact that makes your MVP viable is: `PreToolUse` fires **before** the tool call executes, it can match `Write`, and the hook receives `tool_name`, `tool_input`, and `tool_use_id`. For `Write`, the input includes `file_path` and `content`. `PreToolUse` can return `allow`, `deny`, or `ask`, and can also modify input with `updatedInput`. `PermissionRequest` is secondary; it fires only when a permission dialog is about to be shown, while `PreToolUse` fires before tool execution regardless of permission status. `PostToolUse` fires after a tool succeeds. ([Claude API Docs][1])

# Claude Code write-gate MVP spec

## 1. Keep the architecture exactly this shape

Your MVP should stay as:

`User -> Claude Code -> Hook check -> Script(py) -> Knowledge Gate (Agg.md + global.md + Gemini) -> either Exec or QA Loop -> Result -> update competence model`

And not more than that.

Concretely:

* **Claude Code** is the only agent/runtime.
* **Hook check** is one Claude `PreToolUse` hook on `Write`.
* **Script (py)** is the single entrypoint that does interception logic.
* **Agg.md** is the aggregated context packet for this write attempt.
* **global.md** is the competence model store.
* **Gemini** is the external evaluator/router.
* **Open react page** is the question loop UI, with terminal fallback later if desired.
* **Exec** means “the write is now allowed to happen.”
* **Result** means pass / fail / fail-3x and the competence update.

That matches your board drawings: one hot path for allow, one side loop for blocked/questioned writes, and one competence update path at the end.

## 2. MVP scope: intercept only `Write`

Do **not** start with `Edit` or `MultiEdit`.

The first MVP matcher should be only:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/write_gate.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/write_post.py"
          }
        ]
      }
    ]
  }
}
```

This is aligned with Claude’s documented matcher model, where `PreToolUse` and `PostToolUse` filter by tool name, and `Write` is one of the supported tool names. ([Claude API Docs][1])

## 3. What the hook actually intercepts

The `Write` hook receives:

* `tool_name`
* `tool_input`
* `tool_use_id`
* common fields like `session_id`, `cwd`, `transcript_path`, `permission_mode`

For `Write`, `tool_input` includes:

* `file_path`
* `content`

So your script can read the **current file** from disk, compare it to the proposed `content`, build old/new code, and decide **before Claude writes the file**. ([Claude API Docs][1])

That is the exact place your diagram’s “Hook check” and “Prompt old code/new code” belong.

## 4. Concrete dataflow

### Step A: Claude proposes a write

Claude decides to use `Write(file_path, content)`.

### Step B: Hook check runs

Claude fires `PreToolUse` for `Write`.

### Step C: `write_gate.py` builds the packet

The script:

1. reads hook JSON from stdin
2. extracts `file_path`, `content`, `session_id`, `cwd`, `tool_use_id`
3. reads the current file contents if the file already exists
4. computes:

   * `old_code`
   * `new_code`
   * unified diff
5. writes/refreshes `Agg.md`

### Step D: Knowledge Gate runs

The script loads:

* `Agg.md`
* `global.md`

Then calls Gemini with:

* attempted write
* old/new code
* diff summary
* selected surrounding code
* relevant competence entries

### Step E: Gemini returns one of two classes

For MVP, keep Gemini outputs simple:

* `ALLOW`
* `BLOCK`

If `BLOCK`, include:

* why blocked
* which competence entries were relevant
* question prompts for the QA loop

### Step F1: Allow path

The hook returns Claude `permissionDecision: "allow"`.

Claude then performs the original `Write`.

### Step F2: Block path

The hook returns Claude `permissionDecision: "deny"` with a reason that tells Claude not to perform the write yet.

Separately, the script opens the React question page and hands it the question packet.

### Step G: QA loop

The React page asks the questions.
Possible outcomes:

* pass
* fail
* fail x3 => decline/bounce

### Step H: Result + model update

Write the result into:

* `Result`
* `global.md`

If pass, mark the relevant competence entries upward.
If fail repeatedly, lower confidence or keep them unresolved.

That is almost one-for-one with your diagram.

## 5. Minimal internal objects

Keep them tiny.

### Hook payload

Raw Claude input, unchanged.

### Aggregation packet

Persist to `Agg.md` as the human-readable working packet.

Suggested structure:

````md
# Write Attempt

## Metadata
- session_id:
- tool_use_id:
- cwd:
- file_path:
- timestamp:

## User prompt
<best-effort latest prompt excerpt>

## Old code
```lang
...
````

## New code

```lang
...
```

## Diff

```diff
...
```

## Surrounding code

```lang
...
```

## Recent context

* relevant recent assistant/user turns
* previous mentor outcomes if any

````

### Competence store
Keep `global.md` as one markdown file for MVP, not a database.

Suggested shape:

```md
# Competence Model

## concept: recursion
- mastery: 0.72
- confidence: 0.66
- last_updated: 2026-03-21
- evidence:
  - passed explanation on base case
  - failed earlier on stack growth

## concept: sql joins
...
````

### Gemini output

Keep it rigid:

```json
{
  "decision": "ALLOW" | "BLOCK",
  "reason": "string",
  "concepts": ["..."],
  "questions": ["...", "..."],
  "competence_updates_suggested": [
    {
      "concept": "recursion",
      "direction": "up" | "down" | "hold",
      "delta": 0.1
    }
  ]
}
```

## 6. Claude-native control behavior

Use only these Claude behaviors in MVP.

### Allow path

Return:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Knowledge gate approved write."
  }
}
```

### Block path

Return:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Do not perform this write yet. The user must complete the knowledge-gate questions first."
  }
}
```

Claude documents that in `PreToolUse`, `allow` skips the permission prompt, `deny` prevents the tool call, and for `deny` the reason is shown to Claude. ([Claude API Docs][1])

That is exactly what you want for the “block change -> question loop” branch.

## 7. Why `PermissionRequest` is not the primary choke point

Do **not** put the MVP on `PermissionRequest`.

Use it only later if you want extra confirmation behavior.

Reason: `PermissionRequest` runs only when Claude is about to show a permission dialog, while `PreToolUse` runs before tool execution regardless of permission status. So `PreToolUse` is the reliable interception boundary for “grab writes before they land.” ([Claude API Docs][1])

## 8. The question loop, respecting your drawing

The question loop should stay separate from Claude’s internal tool call.

Flow:

`BLOCK -> open window -> ask Q/A -> pass or fail -> result -> update model`

### MVP rules

* ask 1–3 questions max
* if pass: record success and allow the next retry
* if fail: give brief feedback and retry
* after 3 failures: decline / bounce

That maps directly to your whiteboard “Fail x3 -> Decline/Bounce -> Model Update”.

### Important implementation detail

Do **not** try to keep the original blocked `Write` suspended.
Instead:

1. block the write
2. run the QA loop out of band
3. on pass, Claude retries naturally or the user re-prompts
4. the hook consults the freshly updated model and allows

That keeps the hook simple and avoids trying to resume a blocked tool call.

## 9. Minimal file layout

Use the whiteboard’s hook-entrypoint idea exactly:

```text
.claude/
  settings.json
  hooks/
    write_gate.py
    write_post.py
mentor/
  Agg.md
  global.md
  qa/
    pending/
    results/
  web/
    react-page/
```

This respects your “hook / event type / entrypoint: .exe / .py / .sh” note. Start with `.py`.

## 10. `write_gate.py` responsibilities

Keep it narrow.

### Inputs

stdin Claude hook JSON

### Reads

* current file contents
* `mentor/global.md`
* maybe the latest transcript slice if needed

### Writes

* `mentor/Agg.md`
* pending QA packet if blocked

### Calls

* Gemini API / CLI

### Returns to Claude

* `allow` or `deny`

Pseudo-flow:

```python
def main():
    event = json.load(sys.stdin)
    if event["tool_name"] != "Write":
        return allow_exit()

    file_path = event["tool_input"]["file_path"]
    new_code = event["tool_input"]["content"]
    old_code = read_existing(file_path)

    agg = build_agg_md(event, old_code, new_code)
    save("mentor/Agg.md", agg)

    competence = load_global_md("mentor/global.md")
    verdict = call_gemini(agg, competence)

    if verdict.decision == "ALLOW":
        print(pretool_allow("Knowledge gate approved write."))
        return

    save_pending_qa_packet(verdict, agg)
    launch_react_page(verdict)
    print(pretool_deny(
        "Do not perform this write yet. The user must complete the knowledge-gate questions first."
    ))
```

## 11. `write_post.py` responsibilities

This runs only after a successful `Write`, because Claude’s `PostToolUse` fires after a tool succeeds. ([Claude API Docs][1])

Use it only for:

* logging the write happened
* attaching outcome to the current attempt
* maybe lightweight competence reinforcement if the write came after a pass

Do not put policy here.

## 12. Worktree support: keep out of MVP hot path

Claude does have native `WorktreeCreate` / `WorktreeRemove`, and `WorktreeCreate` fires when using `--worktree` or `isolation: "worktree"`. ([Claude API Docs][1])

But for **this** MVP, I would keep worktrees out of the default path.

Your board shows a direct:
`Claude -> Hook check -> Knowledge Gate -> Exec or QA Loop`

So only introduce worktrees later for high-risk tasks. Not now.

## 13. Refined spec, condensed

Here is the tight spec version.

### System invariant

No Claude `Write` reaches disk unless the `Write` hook returns `allow`.

### Primary event

Claude `PreToolUse` on `Write`.

### Primary script

`.claude/hooks/write_gate.py`

### Knowledge gate inputs

* proposed write
* old code
* new code
* diff
* surrounding code
* recent prompt context
* `global.md`

### Knowledge gate outputs

* `ALLOW`
* `BLOCK` + questions + competence update suggestions

### Block behavior

* deny the write in Claude
* open React QA page
* ask up to 3 questions
* pass => update competence positively
* fail x3 => decline/bounce and update negatively or hold

### Allow behavior

* return `permissionDecision: "allow"`
* let Claude’s original write happen
* log via `PostToolUse`

### Persistent artifacts

* `mentor/Agg.md`
* `mentor/global.md`
* `mentor/qa/pending/*`
* `mentor/qa/results/*`

## 14. One concrete recommendation

Use this exact first hook config:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/write_gate.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/write_post.py"
          }
        ]
      }
    ]
  }
}
```

That gives you the smallest possible Claude-native implementation matching your diagram: **one write chokepoint, one Python gate, one aggregate markdown file, one competence markdown file, one Gemini decision, one QA loop.**

I can turn this into a repo-ready `docs/claude-write-gate-mvp.md` next, with the sample Python hook skeleton and the `Agg.md` / `global.md` schemas.

[1]: https://docs.anthropic.com/en/docs/claude-code/hooks "Hooks reference - Claude Code Docs"

