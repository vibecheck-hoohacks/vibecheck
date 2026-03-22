# VibeCheck: Knowledge-Gated Claude Code Workflow

**Agent**: Claude Code  
**Objective**: Build a mentor-gated coding workflow that intercepts AI-proposed code edits, validates user understanding, and gates execution.

---

## Architecture

```
User Prompt → Claude Code → PreToolUse Hook → Python Gatekeeper 
    → Knowledge Gate (Agg.md + global.md + Gemini) 
    → Allow Exec OR QA Loop → Result → Update Competence
```

### Key Invariants
- **No Write/Edit reaches disk unless the hook returns `allow`**
- **PreToolUse** fires before tool execution, regardless of permission status
- **QA loop runs out-of-band** — do not try to suspend the blocked tool call

---

## 1. Hook Interception (PreToolUse)

### Configuration (`.claude/settings.json`)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [{ "type": "command", "command": "python3 .vibecheck/hooks/write_gate.py" }]
      },
      {
        "matcher": "Edit",
        "hooks": [{ "type": "command", "command": "python3 .vibecheck/hooks/edit_gate.py" }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [{ "type": "command", "command": "python3 .vibecheck/hooks/write_post.py" }]
      }
    ]
  }
}
```

### Hook Payload (stdin JSON)

Claude sends this to your script:
- `tool_name` — "Write" or "Edit"
- `tool_input` — includes `file_path` and `content` (for Write) or edit parameters (for Edit)
- `tool_use_id` — unique identifier for this tool call
- `session_id`, `cwd`, `permission_mode`

### Write Gate Responsibilities

```
INPUTS:
  - stdin: Claude hook JSON
  - current file contents (read from disk)

ACTIONS:
  1. Parse hook payload
  2. Read existing file content if file exists
  3. Build PatchProposal with old/new code + unified diff
  4. Write to .vibecheck/Agg.md
  5. Load .vibecheck/global.md
  6. Call Gemini evaluation
  7. If ALLOW → return hook permissionDecision: "allow"
  8. If BLOCK → save pending QA packet, launch React page, return "deny"

RETURNS TO CLAUDE:
  - allow: { "hookSpecificOutput": { "hookEventName": "PreToolUse", "permissionDecision": "allow", "permissionDecisionReason": "..." } }
  - deny: { "hookSpecificOutput": { "hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..." } }
```

---

## 2. Competence Model (global.md)

**Location**: `~/.vibecheck/global.md` (persistent across projects)

```markdown
# Competence Model

| Skill | Score | Last Tested | Notes |
|-------|-------|-------------|-------|
| async_programming | 0.7 | 2026-03-21 | Understands `await` behavior |
| recursion | 0.8 | 2026-03-20 | Good on base cases |
| sql_injection | 0.3 | 2026-03-19 | Needs work on parameterized queries |
| react_hooks | 0.6 | 2026-03-21 | Understands useEffect dependencies |

## concept: <name>
- mastery: 0.0–1.0
- confidence: 0.0–1.0
- last_updated: YYYY-MM-DD
- evidence:
  - passed explanation on <concept>
  - failed earlier on <concept>
```

### Update Rules

| Outcome | Delta |
|---------|-------|
| Pass on 1st try | +0.15 |
| Pass on 2nd try | +0.08 |
| Pass on 3rd try | +0.03 |
| Fail 3x | -0.10 |
| Successful guided implementation | +0.20 |
| Patch later failed/reverted | -0.15 |

---

## 3. Aggregation Packet (Agg.md)

**Location**: `.vibecheck/Agg.md` (per-session)

```markdown
# Write Attempt: <timestamp>

## Metadata
- session_id:
- tool_use_id:
- cwd:
- file_path:

## User Prompt
<latest prompt excerpt>

## Old Code
```lang
<code here>
```

## New Code
```lang
<code here>
```

## Unified Diff
```diff
<diff here>
```

## Surrounding Code
```lang
<code context>
```

## Relevant Competence Entries
- async_programming: 0.7 (relevant)
- recursion: 0.8 (not relevant)
```

---

## 4. Knowledge Gate (Gemini Evaluation)

### Input to Gemini

```json
{
  "proposed_write": { "file_path": "...", "content": "..." },
  "old_code": "...",
  "new_code": "...",
  "diff_summary": "...",
  "competence_entries": [...],
  "relevant_memory": [...]
}
```

### Gemini Output (strict JSON)

```json
{
  "decision": "ALLOW | BLOCK | CONDITIONAL",
  "confidence": 0.0–1.0,
  "missing_concepts": ["async_programming"],
  "reason": "Why this decision",
  "questions": [
    {
      "text": "How does async/await handle errors in this code?",
      "options": ["A: ...", "B: ...", "C: ...", "D: ..."],
      "correct_index": 0,
      "rubric": "Key concept being tested"
    }
  ],
  "competence_updates": [
    { "concept": "async_programming", "direction": "up", "delta": 0.1 }
  ]
}
```

### Decision Logic

```
ALLOW:
  - competence ≥ thresholds AND risk is low
  - Gemini confidence > 0.8

BLOCK:
  - competence < thresholds AND missing concepts detected
  - Trigger QA loop

CONDITIONAL:
  - Borderline competence
  - Ask 1 validation question before execution
```

---

## 5. QA Loop (Terminal + React Fallback)

### Flow

```
BLOCK → Open React page (or terminal fallback)
      → Ask 1-3 mechanism questions
      → Pass/Fail/Retry (max 3)
      → Result → Update model
```

### Question Design Requirements

- **Mechanism over trivia** — ask "how does this work?" not "what is X?"
- **Test reasoning** — edge cases, failure modes, why the fix works
- **Plausible distractors** — wrong answers reflect common misunderstandings
- **Scaffold by attempt**:
  - Attempt 1: Conceptual + mechanism
  - Attempt 2: More guided, narrower scope
  - Attempt 3: Almost direct hinting

### Outcomes

| Result | Action |
|--------|--------|
| Pass | Allow execution, update competence positively |
| Fail 3x | Proceed with warning, update competence negatively |

### Terminal Fallback

If React UI is not feasible:
- Print question to stdout
- Read answer from stdin
- Use numbered options (1-4)

---

## 6. Policy Engine Rules

### Hard-Stops (ALWAYS block, no questions)

- Auth/secrets/crypto operations
- Schema migrations
- Infra/deployment config
- Concurrency primitives
- Destructive operations (rm -rf, DROP TABLE)

### Soft-Gates (Question gate)

- New library/framework patterns
- Complex async logic
- Security-sensitive patterns (not hard-stops)
- Broad refactors

### Auto-Allow

- Low-risk, small scope
- User has strong relevant competence
- No sensitive paths touched

---

## 7. Execution Layer

### Apply Only After

1. Policy engine returned ALLOW, or
2. QA loop passed, or
3. User explicitly proceeded after 3 failures

### Post-Apply Verification

- Syntax parse
- Lint if configured
- Typecheck if configured
- Run targeted tests if available

### If Verification Fails

- Record failure
- Return structured error
- Do NOT silently continue
- Reduce competence confidence

---

## 8. Project Structure

```
.vibecheck/
├── hooks/
│   ├── write_gate.py      # PreToolUse handler for Write
│   ├── write_post.py      # PostToolUse handler
│   └── edit_gate.py       # PreToolUse handler for Edit
├── mentor/
│   ├── Agg.md             # Current session aggregation
│   └── global.md          # Persistent competence model
├── qa/
│   ├── pending/           # Pending QA packets
│   └── results/           # Completed QA results
├── web/
│   └── react-page/        # React QA UI (optional)
├── core/
│   ├── policy_engine.py   # Decision logic
│   ├── gemini_client.py   # Gemini API wrapper
│   ├── patch_analyzer.py  # Diff analysis
│   ├── competence.py      # Competence model ops
│   └── aggregator.py      # Memory retrieval
└── tests/
```

---

## 9. End-to-End Flow

```python
def handle_pre_tool_use(event):
    # 1. Intercept
    if event["tool_name"] not in ["Write", "Edit"]:
        return allow(event)
    
    # 2. Build PatchProposal
    old_code = read_file(event["tool_input"]["file_path"])
    new_code = event["tool_input"]["content"]
    diff = compute_diff(old_code, new_code)
    
    # 3. Persist aggregation
    save_Agg_md(event, old_code, new_code, diff)
    
    # 4. Load competence
    competence = load_global_md()
    
    # 5. Evaluate
    verdict = gemini_evaluate(Agg.md, competence)
    
    # 6. Decision
    if verdict["decision"] == "ALLOW":
        return allow(event, "Knowledge gate approved.")
    
    # 7. Block → QA Loop
    save_pending_qa(verdict)
    open_react_page(verdict)
    return deny(event, "Complete knowledge-gate questions first.")

def handle_post_tool_use(event):
    # Log successful write
    log_write(event)
    # Attach outcome to current attempt
    # Lightweight competence reinforcement if applicable
```

---

## 10. Test Scenarios

### Scenario 1: Low-Risk Patch → Allow
```
User: "Add a print statement"
Competence: print/statements = 0.9
Expected: ALLOW immediately
```

### Scenario 2: Async Logic → Question Gate
```
User: "Make this function async and add await"
Competence: async_programming = 0.3
Expected: BLOCK → Question on async behavior → Pass after 2 attempts → ALLOW
```

### Scenario 3: Secrets Change → Hard Block
```
User: "Update the API key in config.py"
File: config.py (sensitive path)
Expected: DENY without questions → Manual review required
```

---

## Implementation Order

1. Hook interception (PreToolUse on Write)
2. PatchProposal builder + Agg.md
3. Competence model (global.md)
4. Gemini client (mockable)
5. Policy engine (basic rules)
6. QA loop (terminal-first)
7. React UI fallback
8. Grading + retry logic
9. Competence updates
10. Post-apply verification
11. End-to-end integration
12. Hardening pass

---

## Key Constraints

- **Never bypass the gate** — execution only after allow/pass
- **File-based state** — no database for MVP
- **Local-first** — no cloud dependencies
- **Deterministic core** — LLM assists but hard rules stay outside Gemini
- **Auditable** — all decisions logged
- **Keep it simple** — working MVP > speculative framework
