#!/bin/bash
set -euo pipefail

# VibeCheck Demo — Step 0: Setup
# Requires: OPENROUTER_API_KEY environment variable

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=== VibeCheck Demo Setup ==="
echo ""

# 1. Auth — save API key from environment
echo "[1/4] Configuring OpenRouter API key..."
uv run python -m cli.main auth --from-env
echo ""

# 2. Init competence model — max competence
echo "[2/4] Initializing competence model (max preset)..."
uv run python -m cli.main cm init --preset max
echo ""

# 3. Bootstrap Claude Code hook at repo root
echo "[3/4] Bootstrapping Claude Code hook at repo root..."
uv run python -m cli.main cc init
echo ""

# 4. Bootstrap Claude Code hook inside demo/sample_project
echo "[4/4] Bootstrapping Claude Code hook inside demo/sample_project..."
uv run python -m cli.main cc init --target-dir demo/sample_project
echo ""

echo "=== Setup complete. Ready for step 1. ==="
