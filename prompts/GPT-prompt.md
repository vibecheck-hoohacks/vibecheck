## 🔧 SYSTEM PROMPT: Build Knowledge-Gated Claude Code Extension

You are building a **Claude Code plugin (gatekeeper)** that intercepts tool execution and enforces a **knowledge-based permission system** before allowing code changes to execute.

### 🎯 Objective

Implement a **pre-tool execution hook system** that:
1. Intercepts Claude Code tool usage (patch/apply changes).
2. Evaluates whether the user understands the code changes.
3. Uses a **competence model** + **LLM evaluation (Gemini)**.
4. Routes to a **QA loop** if competence is insufficient.
5. Updates competence over time.

---

## 🧩 Core Functional Flow

### 1. Interception Layer
- Hook into Claude Code via:
  - `preToolUse`
  - `permissionRequest`
- Entry point: `gatekeeper.py`

### 2. Input to Gatekeeper
- User prompt
- Proposed code diff (old vs new)
- Current competence model (`global.md`)
- Aggregated history (`agg.md`)

---

### 3. Competence Evaluation (Gemini)

Call Gemini with:
- User prompt
- Code diff
- Competence model

Gemini must return structured JSON:

%%%json
{
  "decision": "ALLOW | BLOCK | CONDITIONAL",
  "confidence": 0.0-1.0,
  "missing_concepts": ["concept1", "concept2"],
  "reasoning": "...",
  "competence_updates": [
    {"concept": "...", "delta": +0.1}
  ]
}
%%%

---

### 4. Decision Logic

#### ✅ ALLOW
→ Execute tool immediately

#### ❌ BLOCK
→ Send to QA loop

#### ⚠️ CONDITIONAL
→ Ask 1–3 validation questions before execution

---

### 5. QA Loop

If blocked:

- Generate questions using LLM
- Present via:
  - CLI (default)
  - Optional React UI

Loop:
- Ask question
- Evaluate answer
- Retry up to 3 times

Outcomes:
- PASS → allow execution
- FAIL (3x) → block execution

---

### 6. Competence Model Update

After:
- Successful execution OR
- QA pass

Update:
- `global.md` (concept strengths)
- `agg.md` (interaction history)

---

## 🧱 Implementation Constraints

- Use **Python** for backend logic
- Keep system modular and testable
- Use **file-based state (Markdown/JSON)** for MVP
- Mock Gemini API if needed
- Ensure all decisions are deterministic + logged

---

## 📦 Deliverables

Build a working MVP with:
1. Hook interception
2. Gemini evaluation (mocked allowed)
3. QA loop (CLI-based)
4. Competence tracking
5. End-to-end flow working on a sample patch

---

## 🧪 Testing Scenario

Simulate:
- User submits code patch involving "async programming"
- Competence model lacks async knowledge
→ System should:
  - Block
  - Ask questions
  - Allow after correct answers

---

## ⚙️ Non-Goals (for MVP)

- No authentication
- No database (file-based only)
- No full frontend required (CLI is enough)

---

# 📁 Suggested Project Structure

```
.logicguard/
│
├── gatekeeper.py
├── config.py
│
├── hooks/
│   ├── pre_tool.py
│   └── permission.py
│
├── evaluator/
│   ├── gemini_client.py
│   ├── prompt_builder.py
│   └── parser.py
│
├── competence/
│   ├── model.py
│   ├── updater.py
│   └── schema.py
│
├── qa_loop/
│   ├── orchestrator.py
│   ├── question_gen.py
│   ├── evaluator.py
│   └── cli_interface.py
│
├── execution/
│   ├── executor.py
│   └── decision_engine.py
│
├── memory/
│   ├── agg.md
│   └── global.md
│
├── utils/
│   ├── diff_parser.py
│   ├── logger.py
│   └── file_io.py
│
├── tests/
│   ├── test_gatekeeper.py
│   ├── test_qa_loop.py
│   └── test_evaluator.py
│
└── README.md
```

---

# 🔄 Competence Model Example

%%%markdown
# Competence Model

## Concepts
- async_programming: 0.2
- recursion: 0.8
- REST_APIs: 0.6
%%%

---

# 🔄 Aggregation File Example

%%%markdown
# Interaction History

## Session 1
- Prompt: ...
- Missing Concepts: async_programming
- Outcome: PASS after 2 attempts
%%%

---

# 🚀 Minimal Execution Flow

```
def handle_pre_tool_use(input_data):
    prompt = input_data["prompt"]
    diff = input_data["diff"]

    competence = load_competence()

    evaluation = gemini_evaluate(prompt, diff, competence)

    decision = evaluation["decision"]

    if decision == "ALLOW":
        return execute()

    if decision in ["BLOCK", "CONDITIONAL"]:
        result = run_qa_loop(evaluation["missing_concepts"])

        if result == "PASS":
            update_competence()
            return execute()
        else:
            return deny()
```
