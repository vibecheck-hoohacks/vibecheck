# Failure Modes — Phase 4 Notes

## Tested failure paths

| Scenario | Expected | Verified |
|----------|----------|----------|
| Malformed JSON payload | `HookPayloadError("not valid JSON")` | Yes |
| Non-object JSON (array) | `HookPayloadError("must decode to an object")` | Yes |
| Empty string payload | `HookPayloadError("empty")` | Yes |
| Whitespace-only payload | `HookPayloadError("empty")` | Yes |
| Missing competence YAML | Creates default model gracefully | Yes |
| Blocked gate, no QA packet | `StateValidationError("QA packet")` | Yes |
| Fail 3x → competence dock | Score decremented by 0.06, evidence recorded | Yes |
| Non-mutation tool | Bypass, no artifacts created | Yes |
| Empty tool_input | Error raised cleanly | Yes |
| Edit missing old_string | `HookPayloadError` | Yes |

## Untested failure paths (known gaps)
- Disk full during YAML write
- Competence model YAML with corrupted/invalid content
- Concurrent hook invocations writing to same state files
- Extremely large payloads (memory pressure)
- Network errors if/when LLM adapter goes remote
