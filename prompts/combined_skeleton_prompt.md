# 🔧 SYSTEM PROMPT: Build VibeCheck (Knowledge-Gated Claude Code Tool)

You are an expert Python systems engineer. Build a **terminal-based Knowledge-Gated execution system** called **VibeCheck** that integrates with Claude Code via hooks and enforces a **competence-aware permission layer** before applying code changes.

This system must follow this architecture:

**Knowledge Gate → QA Loop → Execution → Competence Update**

It combines:
- Heuristic analysis (deterministic)
- LLM evaluation (Gemini, optional/mockable)
- File-based learning system

---

# 🎯 High-Level Objective

Build a system that:

1. Intercepts Claude Code tool usage (patch/apply)
2. Evaluates whether the user understands the code changes
3. Uses:
   - A **competence model (file-based)**
   - **LLM evaluation (Gemini)**
   - **Heuristic diff analysis**
4. Blocks or conditions execution if knowledge is insufficient
5. Runs a **QA loop to validate understanding**
6. Learns over time by updating competence

---

# 🧠 SYSTEM ARCHITECTURE

## 1. Entry Point (Hook Handler)

Hook into Claude Code via:
- `preToolUse`
- `permissionRequest`

Main function:

    def handle_code_event(prompt: str, diff: str, context: str) -> str:
        ...

This is the **single entry point**.

---

## 2. Inputs

Persist all inputs to:

`memory/context.md`

    # Context

    ## User Prompt
    ...

    ## Code Diff
    ...

    ## Surrounding Code
    ...

Also load:

- `memory/competence.md`
- `memory/agg.md`

---

## 3. Competence Model

File: `memory/competence.md`

    # Competence Model

    ## Topics
    Async Programming: 40
    Python Basics: 85
    Diff Understanding: 60

    ## History
    [timestamp] Topic: Async | Result: fail | Attempts: 3

### Required Functions

- `load_competence()`
- `update_competence(topic, delta, attempts)`
- `infer_topics_from_diff(diff)`
- `get_required_threshold(topic)`

---

## 4. Dual Evaluation System

### A. Heuristic Analyzer (Deterministic)

Analyze diff for topics:

Examples:
- `async/await` → Async Programming ≥ 60
- decorators → Python ≥ 70
- complex diffs → Diff Understanding ≥ 65

Returns:

    {
      "topics": ["async_programming"],
      "required_levels": {"async_programming": 60},
      "confidence": 0.7
    }

---

### B. Gemini Evaluation (LLM)

Input:
- user prompt
- diff
- competence

Output (STRICT JSON):

    {
      "decision": "ALLOW | BLOCK | CONDITIONAL",
      "confidence": 0.0,
      "missing_concepts": ["async_programming"],
      "reasoning": "...",
      "competence_updates": [
        {"concept": "async_programming", "delta": 0.1}
      ],
      "explanation": "..."
    }

Must be **mockable**.

---

## 5. Decision Engine (Fusion Layer)

Combine heuristic + Gemini.

### Rules:

#### ALLOW
- Competence ≥ thresholds
- OR Gemini confident

→ Execute immediately

#### BLOCK
- Competence too low
- AND missing concepts detected

→ Trigger QA loop

#### CONDITIONAL
- Borderline competence

→ Ask validation questions first

---

## 6. QA LOOP

Triggered on BLOCK or CONDITIONAL.

### Flow:

1. Generate explanation (Gemini or fallback)
2. Generate question:
   - Multiple choice
   - 4 options
   - 1 correct

3. Loop (max 3 attempts):
   - Ask user via CLI
   - Evaluate answer
   - Adapt difficulty

---

### Outcomes

| Result | Action |
|------|--------|
| PASS | Allow execution |
| FAIL (3x) | Allow with penalty (default) |

---

## 7. Competence Updates

Rules:

- 1 attempt → +10
- 2 attempts → +5
- 3 attempts → -5
- Fail → -10

Also apply Gemini updates if present.

Persist to:
- `competence.md`
- `agg.md`

---

## 8. Execution Layer

If allowed:

- Apply patch using Claude Code
- Log full decision path

---

## 9. Logging

Log everything:

- Inputs
- Heuristic output
- Gemini output
- Decisions
- QA attempts
- Competence updates

---

# 📁 PROJECT STRUCTURE

    vibecheck/
    │
    ├── cli.py
    ├── gatekeeper.py
    ├── hook_handler.py
    │
    ├── competence/
    │   ├── model.py
    │   ├── updater.py
    │   └── schema.py
    │
    ├── evaluator/
    │   ├── gemini_client.py
    │   ├── heuristic_analyzer.py
    │   ├── fusion_engine.py
    │   └── parser.py
    │
    ├── qa_loop/
    │   ├── orchestrator.py
    │   ├── question_engine.py
    │   ├── evaluator.py
    │   └── cli_interface.py
    │
    ├── execution/
    │   ├── executor.py
    │   └── decision_engine.py
    │
    ├── memory/
    │   ├── competence.md
    │   ├── agg.md
    │   └── context.md
    │
    ├── utils/
    │   ├── diff_parser.py
    │   ├── logger.py
    │   └── file_io.py
    │
    └── tests/

---

# 🔄 END-TO-END FLOW

    def handle_code_event(prompt, diff, context):

        save_context(prompt, diff, context)

        competence = load_competence()

        heuristic = analyze_diff(diff)
        gemini = gemini_evaluate(prompt, diff, competence)

        decision = fuse(heuristic, gemini, competence)

        if decision == "ALLOW":
            execute()
            update_competence(...)
            return

        if decision in ["BLOCK", "CONDITIONAL"]:
            result = run_qa_loop(gemini["missing_concepts"])

            update_competence(result)

            if result == "PASS":
                execute()
            else:
                deny()

---

# 🧪 TEST SCENARIO

Simulate:

- Code diff includes async/await
- Competence:
  - Async Programming = 30

Expected behavior:

1. BLOCK triggered  
2. QA loop starts  
3. User answers questions  
4. PASS after 2 attempts  
5. Competence updated  
6. Execution allowed  

---

# ⚙️ REQUIREMENTS

- Python 3.10+
- CLI-based (Typer preferred)
- Local-first (no DB)
- Gemini optional
- Clean modular design
- Type hints everywhere
- Fully testable

---

# 🚀 DELIVERABLES

Provide:

1. Full working codebase  
2. Example files:
   - `competence.md`
   - `context.md`  
3. Example CLI session  
4. Mock Gemini implementation  
5. End-to-end working demo  

---

# 🔥 DESIGN PRINCIPLES

- Deterministic core, LLM-assisted reasoning  
- Never blindly block — always teach  
- Validate understanding before execution  
- Continuous learning system  