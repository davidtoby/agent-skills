#!/usr/bin/env bash
set -euo pipefail

PROVIDER_ID="${PROVIDER_ID:-litellm}"
MODEL_ID="${MODEL_ID:-gemini-3.1-pro-preview}"
OPENCODE_BIN="${OPENCODE_BIN:-$HOME/.opencode/bin/opencode}"
RUN_SMOKE_TEST="${RUN_SMOKE_TEST:-0}"

resolved="$(command -v opencode || true)"
echo "command -v opencode => ${resolved:-not found}"

if [[ -n "$resolved" && "$resolved" != "$OPENCODE_BIN" ]]; then
  echo "WARNING: opencode does not resolve to the expected official binary: $OPENCODE_BIN" >&2
  echo "A wrapper or PATH shadowing may still be active." >&2
fi

if [[ ! -x "$OPENCODE_BIN" ]]; then
  echo "ERROR: Official OpenCode binary not executable: $OPENCODE_BIN" >&2
  exit 1
fi

file "$OPENCODE_BIN"

echo
echo "Checking LiteLLM provider models..."
tmp_models="$(mktemp -t opencode-litellm-models.XXXXXX)"
trap 'rm -f "$tmp_models"' EXIT
"$OPENCODE_BIN" models "$PROVIDER_ID" | tee "$tmp_models"
if ! grep -Fxq "$PROVIDER_ID/$MODEL_ID" "$tmp_models"; then
  echo "ERROR: Expected model not found: $PROVIDER_ID/$MODEL_ID" >&2
  exit 1
fi

echo
echo "Checking OpenAI models still load..."
"$OPENCODE_BIN" models openai | sed -n '1,20p'

if [[ "$RUN_SMOKE_TEST" == "1" ]]; then
  echo
  echo "Running smoke test with $PROVIDER_ID/$MODEL_ID..."
  "$OPENCODE_BIN" run -m "$PROVIDER_ID/$MODEL_ID" "只回答 OK"
else
  echo
  echo "Skipping smoke test. Set RUN_SMOKE_TEST=1 to run one request."
fi

echo
echo "Verification completed. Use /models in the OpenCode TUI to switch models."
