# Claude Code + LiteLLM Quickstart / 中文快速开始

This quickstart covers two cases:

- **Mode A / Wrapper 模式**: keep existing `claude`, add `claude-gemini`
- **Mode B / 主命令切换模式**: back up `~/.claude/settings.json`, then make plain `claude` default to LiteLLM + Gemini

这份 quickstart 适合两种场景：

- **模式 A / Wrapper 模式**：保留原来的 `claude`，新增 `claude-gemini`
- **模式 B / 主命令切换模式**：先备份 `~/.claude/settings.json`，再让普通 `claude` 默认走 LiteLLM + Gemini

Toby's real setup ended up validating **both** modes successfully.

Toby 这次真实验证的结果是：**两种模式都跑通了**。

---

## 1. Mental model / 正确认知

Claude Code 并不是“原生懂 Gemini 名字”。

真正发生的是：

1. Claude Code 继续按 Anthropic Messages API 风格发请求
2. 请求发给 LiteLLM
3. LiteLLM 再转给真正的上游模型
4. 上游可以是 Gemini / Vertex / OpenAI / Anthropic 等

So Claude Code side mostly needs:

- `ANTHROPIC_BASE_URL`
- `ANTHROPIC_AUTH_TOKEN`
- `ANTHROPIC_MODEL`

---

## 2. Verify LiteLLM first / 先确认 LiteLLM 本身没问题

Before touching Claude Code:

```bash
cd /Users/toby/TobyLab/litellm-vertex-proxy
./scripts/service.sh status
lsof -nP -iTCP:4000 -sTCP:LISTEN
```

If `127.0.0.1:4000` is not listening, fix LiteLLM first.

---

## 3. Validate `/v1/messages`, not just `/v1/models`

This is the real proof:

```bash
bash -lc 'source /Users/toby/TobyLab/litellm-vertex-proxy/scripts/env.sh >/dev/null 2>&1
curl -i http://127.0.0.1:4000/v1/messages \
  -H "x-api-key: $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3.1-pro-preview",
    "max_tokens": 32,
    "messages": [{"role": "user", "content": "Reply with exactly: ok"}]
  }''
```

Expected:

```json
{"type":"message","model":"gemini-3.1-pro-preview","content":[{"type":"text","text":"ok"}]}
```

---

## 4. Decide mode / 决定接入模式

### Mode A: wrapper / 模式 A：wrapper

Use this when:
- you do not want to touch the existing main Claude config
- you want reversible parallel access
- other tools may rely on current `claude`

Create:

```text
~/.local/bin/claude-gemini
```

Optional alias:

```bash
alias cgemini="claude-gemini"
```

### Mode B: main `claude` takeover / 模式 B：主 `claude` 接管

Use this when:
- you explicitly want plain `claude` itself to use LiteLLM + Gemini
- replacing `~/.claude/settings.json` is acceptable
- you still keep a backup and preferably also keep `claude-gemini`

Safe rule:

1. backup first
2. rewrite `env`
3. verify `claude -p`
4. keep rollback path

---

## 5. Wrapper mode reference / Wrapper 模式参考

核心点：

- source LiteLLM env
- unset 旧的直连 Vertex Claude 变量
- export `ANTHROPIC_BASE_URL`
- export `ANTHROPIC_AUTH_TOKEN`
- export `ANTHROPIC_MODEL`
- add `--setting-sources project,local`

Reference script is in:

```text
scripts/claude-gemini-wrapper.sh
```

---

## 6. Main-command takeover reference / 主命令切换参考

Target `~/.claude/settings.json` shape:

```json
{
  "theme": "dark",
  "env": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:4000",
    "ANTHROPIC_AUTH_TOKEN": "YOUR_LITELLM_MASTER_KEY",
    "ANTHROPIC_MODEL": "gemini-3.1-pro-preview",
    "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1"
  }
}
```

Helper script:

```bash
scripts/switch-main-to-litellm.sh
```

This script:
- creates a timestamped backup
- preserves top-level fields like `theme`
- rewrites `env` for LiteLLM

---

## 7. Verification / 验证方法

Wrapper mode:

```bash
claude-gemini -p "Reply with exactly: wrapper-ok" --output-format json
```

Main mode:

```bash
claude -p "Reply with exactly: main-ok" --output-format json
```

Look for:
- success
- exact returned text
- `modelUsage.gemini-3.1-pro-preview`

---

## 8. Real Toby result / Toby 的真实结果

This exact setup was validated on Toby's machine with:

- LiteLLM base URL: `http://127.0.0.1:4000`
- model: `gemini-3.1-pro-preview`
- wrapper path: `~/.local/bin/claude-gemini`
- alias: `cgemini`
- main `claude` also switched successfully after backing up `~/.claude/settings.json`

---

## 9. Most common traps / 最常见的坑

- `ANTHROPIC_BASE_URL` 写成 `/v1`
- 只测 `/v1/models`，不测 `/v1/messages`
- 改主配置前不备份
- wrapper 模式忘记 `--setting-sources project,local`
- wrapper 模式忘记 `unset CLAUDE_CODE_USE_VERTEX`

---

## 10. Recommended default advice / 默认建议

If the user did **not** explicitly ask to replace plain `claude`, prefer:

- keep `claude` untouched
- add `claude-gemini`

如果用户**没有明确要求**替换主 `claude`，默认建议仍然是：

- 保留原来的 `claude`
- 新增 `claude-gemini`

If the user explicitly wants plain `claude` to use Gemini, then main-command takeover is valid — just back up first.

如果用户明确要让普通 `claude` 直接走 Gemini，那么主命令切换是合理的 —— 但一定先备份。
