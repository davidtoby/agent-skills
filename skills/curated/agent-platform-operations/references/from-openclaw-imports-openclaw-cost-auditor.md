# Demoted legacy skill: `openclaw-imports/openclaw-cost-auditor`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "openclaw-cost-auditor",
  "installedVersion": "1.0.0",
  "installedAt": 1772264107230
}

```


## `SKILL.md`

````
---
summary: "OpenClaw Cost Auditor: Track API usage, model costs, token burn, and revenue for OpenClaw deployments."
description: "Parse logs, query API metrics, forecast bills, optimize spend with reports & alerts."
triggers:
  - "audit openclaw costs"
  - "openclaw billing"
  - "check API spend"
  - "token usage report"
read_when:
  - "openclaw cost" in message
  - "API auditor" in message
---

# OpenClaw Cost Auditor v1.0.0

## 🎯 Purpose
- Daily/weekly cost reports
- Top models/users by tokens
- Cost per query forecasts
- Optimization recs (quantize, prune)

## 🚀 Quick Start
```
!openclaw-cost-auditor --period last7d --format pdf
```

## Files
- `scripts/audit.py`: Log parser & calculator
- `templates/report.md`: Cost dashboard template

## Integrations
OpenClaw logs, Grok/xAI API, custom providers.

````


## `_meta.json`

```
{
  "ownerId": "kn71bdpm65n26chyt3a7mb5rt180xt74",
  "slug": "openclaw-cost-auditor",
  "version": "1.0.0",
  "publishedAt": 1771598509808
}
```


## `scripts/audit.py`

```
#!/usr/bin/env python3
# OpenClaw Cost Auditor
import glob
import re
import sys

log_dir = sys.argv[1] if len(sys.argv)>1 else '/var/log/openclaw'
total_tokens = 0
for log in glob.glob(f"{log_dir}/*.log"):
    with open(log) as f:
        for line in f:
            tokens = re.findall(r'tokens: (\d+)', line)
            total_tokens += sum(int(t) for t in tokens)
print(f"Total tokens: {total_tokens}")
print(f"Est. cost: ${total_tokens * 0.00001:.2f} (at $10/M)")

```
