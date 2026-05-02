#!/usr/bin/env bash
# Safe Session Cleanup for OpenClaw Agents
# Removes trajectory/debug files while preserving core session state

set -euo pipefail

AGENTS_DIR="${OPENCLAW_AGENTS_DIR:-/workspace/projects/agents}"

echo "OpenClaw Session Cleanup"
echo "========================"
echo ""

for sessions_dir in "$AGENTS_DIR"/*/sessions/; do
    if [ ! -d "$sessions_dir" ]; then
        continue
    fi

    agent_name=$(basename "$(dirname "$sessions_dir")")
    size_before=$(du -sh "$sessions_dir" 2>/dev/null | cut -f1)

    # Count files to be removed
    traj_count=$(find "$sessions_dir" -maxdepth 1 -name "*.trajectory*" 2>/dev/null | wc -l)
    reset_count=$(find "$sessions_dir" -maxdepth 1 -name "*.reset.*" 2>/dev/null | wc -l)
    deleted_count=$(find "$sessions_dir" -maxdepth 1 -name "*.deleted.*" 2>/dev/null | wc -l)
    total=$((traj_count + reset_count + deleted_count))

    if [ "$total" -eq 0 ]; then
        echo "  $agent_name: $size_before (no bloat files)"
        continue
    fi

    echo "  $agent_name: $size_before → cleaning $total files..."

    # Safe removal: only trajectory, reset, and deleted files
    find "$sessions_dir" -maxdepth 1 -name "*.trajectory*" -delete 2>/dev/null || true
    find "$sessions_dir" -maxdepth 1 -name "*.reset.*" -delete 2>/dev/null || true
    find "$sessions_dir" -maxdepth 1 -name "*.deleted.*" -delete 2>/dev/null || true

    size_after=$(du -sh "$sessions_dir" 2>/dev/null | cut -f1)
    echo "  $agent_name: $size_before → $size_after"
done

echo ""
echo "Cleanup complete. Restart Gateway if it was stuck."
