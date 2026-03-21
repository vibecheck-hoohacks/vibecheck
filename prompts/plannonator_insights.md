### Hook Event Ingestion

To capture agent events, the permission hook intercepts the target action and pipes the payload to standard input. Your script reads this stream asynchronously, parses the JSON, and extracts the proposed plan or tool input. By isolating this ingestion phase, the data parsing logic remains strictly decoupled from the core application state, ensuring modularity. Once parsed, the payload is validated and passed to the local server orchestrator.

```typescript
const eventJson = await Bun.stdin.text();
const event = JSON.parse(eventJson);
const planContent = event.tool_input?.plan || "";
const permissionMode = event.permission_mode || "default";
```

### Spawning the Interface

After extracting the payload, the orchestrator spawns an ephemeral HTTP server on an available port. A cross-platform utility then launches the default web browser pointing to this local address. The server holds a pending promise that blocks the main execution thread. It serves the interactive interface and waits for the frontend to submit a POST request containing the user's decision. Once received, the promise resolves, the server gracefully shuts down, and the decision is formatted and written back to standard output for the agent.

```typescript
let resolveDecision: (result: any) => void;
const decisionPromise = new Promise((resolve) => { resolveDecision = resolve; });

const server = Bun.serve({
  port: 0,
  async fetch(req) {
    const url = new URL(req.url);
    if (url.pathname === "/api/feedback" && req.method === "POST") {
      const body = await req.json();
      resolveDecision(body);
      return Response.json({ ok: true });
    }
    return new Response(htmlContent, { headers: { "Content-Type": "text/html" } });
  }
});

await openBrowser(`http://localhost:${server.port}`);
const finalDecision = await decisionPromise;
server.stop();
console.log(JSON.stringify({ hookSpecificOutput: { decision: finalDecision } }));
```

### Capturing Patch Modifications

For code review events, the system must capture current working directory modifications before launching the interface. A dedicated utility spawns a subprocess to execute a version control diff command, capturing the unstaged or uncommitted changes as a raw patch string. This raw patch is then injected into the ephemeral server's state. The frontend retrieves this patch and renders it using a specialized diff viewer, allowing line-by-line annotation without tightly coupling the frontend components to the underlying version control system.

```typescript
import { spawnSync } from "node:child_process";

function captureUncommittedDiff(): string {
  const result = spawnSync("git", ["diff", "--no-ext-diff", "HEAD"], {
    encoding: "utf-8"
  });
  if (result.status !== 0) throw new Error("Diff failed");
  return result.stdout.trim();
}

const rawPatch = captureUncommittedDiff();
```

### Integrating the Knowledge Gate

The knowledge gate intercepts the flow between capturing the patch and presenting the final review interface. The logic is kept modular and isolated. The server sends the raw patch to your external competence model via an API call, requesting targeted educational questions. When the user submits answers, the server forwards them to the competence model for evaluation. Only if the model returns a passing grade does the server output an allow decision, otherwise it issues a denial with corrective feedback.

```python
# /logic/readdata.py
import httpx

async def fetch_evaluation(patch_data: str, user_answers: dict) -> dict:
    payload = {"diff": patch_data, "answers": user_answers}
    async with httpx.AsyncClient() as client:
        response = await client.post("https://competence-model.internal/evaluate", json=payload)
        return response.json()

def process_gate_decision(evaluation_result: dict) -> dict:
    if evaluation_result.get("passed"):
        return {"behavior": "allow"}
    return {"behavior": "deny", "message": evaluation_result.get("feedback")}
```
