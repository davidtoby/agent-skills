#!/usr/bin/env bash
# OpenClaw Feishu Channel Diagnostic
# Run this to get a one-shot health snapshot of all Feishu bots

set -euo pipefail

echo "========================================"
echo "OpenClaw Feishu Channel Diagnostic"
echo "========================================"
echo ""

# 1. Gateway health
echo "--- 1. Gateway Health ---"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "Gateway: HEALTHY (HTTP 200)"
else
    echo "Gateway: UNHEALTHY (HTTP $HTTP_CODE)"
fi
echo ""

# 2. Channel status
echo "--- 2. Feishu Channel Status ---"
openclaw --log-level error channels status --probe 2>/dev/null | grep -E "feishu|running|works|issue" || echo "Could not retrieve channel status"
echo ""

# 3. Pending pairings
echo "--- 3. Pending Pairings ---"
openclaw --log-level error pairing list feishu 2>/dev/null || echo "No pending pairings or command failed"
echo ""

# 4. Plugin status
echo "--- 4. Plugin Status ---"
openclaw --log-level error plugins list 2>/dev/null | grep -E "lark|feishu" || echo "No Feishu plugins found"
echo ""

# 5. Session sizes
echo "--- 5. Agent Session Sizes ---"
for agent_dir in /workspace/projects/agents/*/sessions/; do
    if [ -d "$agent_dir" ]; then
        agent_name=$(basename "$(dirname "$agent_dir")")
        size=$(du -sh "$agent_dir" 2>/dev/null | cut -f1)
        traj_count=$(find "$agent_dir" -name "*.trajectory*" 2>/dev/null | wc -l)
        echo "  $agent_name: $size (trajectory files: $traj_count)"
    fi
done
echo ""

# 6. Recent errors
echo "--- 6. Recent Errors (last 50 lines) ---"
LOGFILE="/tmp/openclaw/openclaw-$(date +%Y-%m-%d).log"
if [ -f "$LOGFILE" ]; then
    grep -i "error\|fail\|reject\|stuck session\|liveness warning" "$LOGFILE" 2>/dev/null | tail -10 || echo "No errors found"
else
    echo "Log file not found: $LOGFILE"
fi
echo ""

echo "========================================"
echo "Diagnostic complete"
echo "========================================"
