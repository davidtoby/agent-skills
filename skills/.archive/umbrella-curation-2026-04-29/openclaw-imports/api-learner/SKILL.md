---
name: api-learner
description: "Workflow for learning site APIs via traffic capture and replacing browser automation with direct curl calls."
metadata: {"openclaw":{"emoji":"📡"}}
---

# API Learner — Browser-to-API Migration

Instead of fighting browser timeouts on heavy sites, you can use **learned API patterns** to make direct `curl` calls. This is faster, more reliable, and avoids CDP timeout issues.

## When to Suggest API Capture

Suggest this to the operator when:
- A site repeatedly causes browser timeouts (heavy SPAs, JS-heavy storefronts)
- You're doing the same browser task repeatedly (search → add to cart → repeat)
- The browser tool fails with "timed out after 20000ms" on a site you use often

Do NOT use API skills for:
- First visits to a new site (need to discover the workflow first)
- CAPTCHA or bot-detection flows
- Checkout / payment flows (the operator handles these manually)
- Sites where you need to see visual layout (e.g., comparing product images)

## How API Learning Works

1. **The operator starts a capture** on the relevant VNC browser port
2. **Normal browsing happens** — manually or via the browser tool
3. **Capture script records** all XHR/Fetch API calls passively
4. **Generator analyzes** the traffic and produces a SKILL.md with endpoint docs
5. **You use curl** with fresh cookies instead of the browser tool

## Using a Generated API Skill

Once an API skill exists (e.g., `api-example`), follow this pattern:

### Step 1: Extract fresh cookies
```bash
COOKIES=$(/opt/OpenClaw/scripts/extract-cookies.js --domain <domain> --port <cdp-port>)
```
The VNC browser must be open and logged into the site. Cookies come from the live browser session.

### Step 2: Make API calls
Use `curl` with the cookie header:
```bash
curl -s 'https://www.example.com/api/search?q=spinach' \
  -H "Cookie: $COOKIES" | python3 -m json.tool
```

### Step 3: Handle failures
- **401/403:** Cookies expired. Re-extract and retry.
- **Changed responses:** API may have been updated. Tell the operator to re-capture.
- **Unexpected errors:** Fall back to the `browser` tool. Report to the operator.

## Starting a New Capture (For the Operator)

To capture traffic from a site:
```bash
# Capture from Mise's browser (port 9222) for 5 minutes
sudo -u OpenClaw /opt/OpenClaw/scripts/capture-api.js --port 9222 --duration 300

# Capture from Headhunter's browser (port 9223) for 5 minutes
sudo -u OpenClaw /opt/OpenClaw/scripts/capture-api.js --port 9223 --duration 300
```

While capture is running, browse the site normally (search, view products, add to cart, etc.). The more workflows you exercise, the more endpoints get captured.

Add `--redact` to strip request bodies containing passwords or payment info.

## Generating a Skill from Captures

```bash
sudo -u OpenClaw /opt/OpenClaw/scripts/generate-api-skill.js --domain example.com
```

This reads the most recent capture file and generates a SKILL.md at:
`/opt/OpenClaw/.openclaw/skills/api-example/SKILL.md`

Review the generated skill, then register it for the relevant agent in `openclaw.json`.

## Maintenance

- **Cookies are ephemeral.** Always extract fresh cookies before each batch of API calls.
- **APIs change.** If a generated skill stops working, re-capture and regenerate.
- **New endpoints.** Run another capture while exercising the new workflow, then regenerate.
- **Capture files** are stored in `/opt/OpenClaw/.openclaw/captures/<domain>/` and can be deleted when no longer needed.
