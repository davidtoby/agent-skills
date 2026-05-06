# Claude Code + LiteLLM Quickstart / 中文快速开始

This quickstart is for the case where:

- Claude Code is already installed
- LiteLLM is already running locally
- LiteLLM already exposes the target model
- you do **not** want to break an existing Hermes / OpenClaw / Claude setup

这份 quickstart 面向已经满足以下前提的场景：

- 你已经安装好了 Claude Code
- 你本机已经有一个可用的 LiteLLM
- LiteLLM 已经能代理到目标模型
- 你**不想破坏**已有的 Hermes / OpenClaw / Claude 其它配置

Toby's successful real-world setup used:

- Claude Code
- through LiteLLM
- to a Vertex AI-backed model
- `gemini-3.1-pro-preview`

Toby 这次的成功案例是：

- Claude Code
- 通过 LiteLLM
- 调用 Vertex AI 后端的
- `gemini-3.1-pro-preview`

LiteLLM project path / 本机 LiteLLM 路径:

```text
/Users/toby/TobyLab/litellm-vertex-proxy
```

LiteLLM base URL / 本机 LiteLLM 地址:

```text
http://127.0.0.1:4000
```

Target model / 目标模型:

```text
gemini-3.1-pro-preview
```

---

## 1. Understand the real architecture / 先理解核心思路

Do **not** think of this as “making Claude Code natively understand Gemini names.”

The correct mental model is:

1. Claude Code still sends Anthropic-style requests
2. It sends them to LiteLLM
3. LiteLLM translates and routes them to the real upstream model
4. In this setup, the real upstream model is:
   - `vertex_ai/gemini-3.1-pro-preview`

不要把这件事理解成“让 Claude Code 原生支持 Gemini 名字”。

正确理解是：

1. Claude Code 仍然按 **Anthropic 风格** 发请求
2. 它把请求发给 LiteLLM
3. LiteLLM 再把请求翻译并路由到真正的上游模型
4. 这里真正的上游模型是：
   - `vertex_ai/gemini-3.1-pro-preview`

So the Claude Code side is mainly about setting:

- `ANTHROPIC_BASE_URL`
- `ANTHROPIC_AUTH_TOKEN`
- `ANTHROPIC_MODEL`

所以 Claude Code 这一侧重点不是改模型能力，而是：

- 配对 `ANTHROPIC_BASE_URL`
- 配对 `ANTHROPIC_AUTH_TOKEN`
- 配对 `ANTHROPIC_MODEL`

---

## 2. Verify LiteLLM first / 先确认 LiteLLM 本身是好的

Before touching Claude Code, confirm LiteLLM itself is healthy:

```bash
cd /Users/toby/TobyLab/litellm-vertex-proxy
./scripts/service.sh status
lsof -nP -iTCP:4000 -sTCP:LISTEN
```

在跑 Claude Code 之前，先确认 LiteLLM 服务本身没问题：

```bash
cd /Users/toby/TobyLab/litellm-vertex-proxy
./scripts/service.sh status
lsof -nP -iTCP:4000 -sTCP:LISTEN
```

If `127.0.0.1:4000` is not listening, fix LiteLLM first.

如果 `127.0.0.1:4000` 没监听，就先修 LiteLLM，不要往 Claude Code 身上找原因。

---

## 3. Validate `/v1/messages`, not just `/v1/models` / 一定要验证 `/v1/messages`，不要只看 `/v1/models`

This is a critical trap.

Many people only verify:

```bash
/v1/models
```

But Claude Code relies much more directly on Anthropic-style:

```bash
/v1/messages
```

这是一个很关键的坑。

很多人只验证：

```bash
/v1/models
```

但 Claude Code 真正更关键的是 Anthropic 风格的：

```bash
/v1/messages
```

Test it first like this:

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

请先这样测：

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

Expected success shape / 成功时你应该看到类似：

```json
{"type":"message","model":"gemini-3.1-pro-preview","content":[{"type":"text","text":"ok"}]}
```

That is the real proof that the Claude Code → LiteLLM path is viable.

这一步成功，才说明 Claude Code 走 LiteLLM 的基础链路是通的。

---

## 4. Why plain `claude` is risky here / 为什么不能直接硬上 `claude`

If your `~/.claude/settings.json` already contains something like:

```json
{
  "env": {
    "CLAUDE_CODE_USE_VERTEX": "1",
    "ANTHROPIC_VERTEX_PROJECT_ID": "...",
    "CLOUD_ML_REGION": "global"
  }
}
```

then plain `claude` may prefer your existing direct Vertex / Anthropic path.

如果你的 `~/.claude/settings.json` 里已经有类似：

```json
{
  "env": {
    "CLAUDE_CODE_USE_VERTEX": "1",
    "ANTHROPIC_VERTEX_PROJECT_ID": "...",
    "CLOUD_ML_REGION": "global"
  }
}
```

那普通的 `claude` 命令很可能会优先走你原来的 **直连 Vertex / Anthropic 路线**。

This creates three common problems:

- you think you are testing LiteLLM, but you are not
- `--model gemini-3.1-pro-preview` may be intercepted by local/provider logic
- you may break a previously working global Claude setup while “fixing” Claude Code

这会导致几个问题：

- 你以为在测 LiteLLM，其实没走 LiteLLM
- `--model gemini-3.1-pro-preview` 可能被本地校验或 provider 路径拦住
- 你为了修 Claude Code，反而把原来能用的全局配置搞乱

So the key decision is:

**Do not smash the global `claude` config. Add a separate entrypoint instead.**

所以这次成功经验的关键决策是：

**不要粗暴改全局 `claude`，而是新增一个单独入口。**

---

## 5. Recommended pattern: `claude-gemini` wrapper / 推荐做法：新增 `claude-gemini` wrapper

Create:

```text
~/.local/bin/claude-gemini
```

推荐新建：

```text
~/.local/bin/claude-gemini
```

Reference implementation / 参考脚本：

```bash
#!/usr/bin/env bash
set -euo pipefail

PROXY_DIR="/Users/toby/TobyLab/litellm-vertex-proxy"

source "$PROXY_DIR/scripts/env.sh" >/dev/null 2>&1

unset CLAUDE_CODE_USE_VERTEX
unset ANTHROPIC_VERTEX_PROJECT_ID
unset CLOUD_ML_REGION
unset ANTHROPIC_DEFAULT_SONNET_MODEL
unset ANTHROPIC_DEFAULT_OPUS_MODEL
unset ANTHROPIC_DEFAULT_HAIKU_MODEL

export ANTHROPIC_BASE_URL="${ANTHROPIC_BASE_URL:-http://127.0.0.1:4000}"
export ANTHROPIC_AUTH_TOKEN="$LITELLM_MASTER_KEY"
export ANTHROPIC_MODEL="${ANTHROPIC_MODEL:-gemini-3.1-pro-preview}"
export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1

extra_args=()
has_setting_sources=0
for arg in "$@"; do
  if [ "$arg" = "--setting-sources" ]; then
    has_setting_sources=1
    break
  fi
done
if [ "$has_setting_sources" -eq 0 ]; then
  extra_args+=(--setting-sources project,local)
fi

exec claude "${extra_args[@]}" "$@"
```

Make it executable / 然后给它执行权限：

```bash
chmod +x ~/.local/bin/claude-gemini
```

Optional alias / 可选：加一个 alias

```bash
alias cgemini="claude-gemini"
```

---

## 6. The most important parameters / 几个最关键的参数解释

### `ANTHROPIC_BASE_URL`
It must be:

```bash
http://127.0.0.1:4000
```

Not:

```bash
http://127.0.0.1:4000/v1
```

因为 Claude Code 会自己访问 `/v1/messages`。

必须是：

```bash
http://127.0.0.1:4000
```

**不要写成：**

```bash
http://127.0.0.1:4000/v1
```

Because Claude Code appends its own API paths such as `/v1/messages`.

### `ANTHROPIC_AUTH_TOKEN`
Use the LiteLLM master key:

```bash
$LITELLM_MASTER_KEY
```

这里应该用 LiteLLM 的 master key。

### `ANTHROPIC_MODEL`
Use the exact LiteLLM-exposed model name:

```bash
gemini-3.1-pro-preview
```

这里直接写 LiteLLM 暴露出来的模型名。

### `--setting-sources project,local`
This is very important.

It prevents this run from loading user-level settings sources and helps avoid `~/.claude/settings.json` stealing the route.

这一步非常重要。

它的作用是：

- 本次启动时，不加载 user 级设置来源
- 避免 `~/.claude/settings.json` 里的旧配置抢路由

### `unset CLAUDE_CODE_USE_VERTEX`
This prevents Claude Code from continuing down the old direct-Vertex route.

这一步是为了防止 Claude Code 继续按你旧的 Vertex 直连链路走。

---

## 7. Prove it with print mode first / 先用 print mode 验证

Do not start with interactive mode.

Run the smallest proof first:

```bash
claude-gemini -p "Reply with exactly: wrapper-ok" --output-format json
```

不要上来就交互式。

先跑一个最小验证：

```bash
claude-gemini -p "Reply with exactly: wrapper-ok" --output-format json
```

If successful, you should see:

- `subtype: success`
- returned text is `wrapper-ok`
- `modelUsage` points to:
  - `gemini-3.1-pro-preview`

如果成功，你应该看到：

- `subtype: success`
- 返回文本是 `wrapper-ok`
- 输出里的 `modelUsage` 指向：
  - `gemini-3.1-pro-preview`

---

## 8. Then use it normally / 确认成功后再正式用

Interactive / 交互式：

```bash
claude-gemini
```

One-shot / 单次命令：

```bash
claude-gemini -p "帮我总结这个仓库" --output-format json
```

Alias / 如果你配了 alias：

```bash
cgemini
```

---

## 9. Why this approach is safe / 这套方案为什么安全

Because it preserves the existing working routes:

- `claude` keeps its old/default behavior
- `claude-gemini` is dedicated to LiteLLM + Gemini
- Hermes Agent's existing LiteLLM chain remains untouched

因为它遵循的是“并行接入，不破坏现状”：

- `claude` 继续保留原来的行为
- `claude-gemini` 专门走 LiteLLM + Gemini
- Hermes Agent 原来的 LiteLLM 调用链完全不动

This is much safer than overwriting `~/.claude/settings.json`.

这比直接去覆盖 `~/.claude/settings.json` 安全得多。

---

## 10. Most common traps / 最常见的坑

### Trap 1: setting `ANTHROPIC_BASE_URL` to `/v1`
Wrong. Use the root:

```bash
http://127.0.0.1:4000
```

### 坑 1：把 `ANTHROPIC_BASE_URL` 写成 `/v1`
错。

应该是根地址：

```bash
http://127.0.0.1:4000
```

### Trap 2: testing only `/v1/models`
Not enough. Also test:

```bash
/v1/messages
```

### 坑 2：只测 `/v1/models`
不够。

还要测：

```bash
/v1/messages
```

### Trap 3: modifying global `claude` settings directly
High risk. Prefer a dedicated wrapper.

### 坑 3：直接修改全局 `claude` 配置
风险很高。

优先用独立 wrapper。

### Trap 4: forgetting `--setting-sources project,local`
Then `~/.claude/settings.json` may steal the route.

### 坑 4：忘记 `--setting-sources project,local`
会导致 `~/.claude/settings.json` 抢路由。

### Trap 5: blaming Claude Code when LiteLLM is down
Check first:

```bash
./scripts/service.sh status
lsof -nP -iTCP:4000 -sTCP:LISTEN
```

### 坑 5：LiteLLM 没起来就怪 Claude Code
先检查：

```bash
./scripts/service.sh status
lsof -nP -iTCP:4000 -sTCP:LISTEN
```

---

## 11. Suggested user-facing summary / 推荐给最终用户的话术

The simplest handoff is:

1. Your existing Claude/Hermes setup was preserved
2. A new dedicated entrypoint was added:
   - `claude-gemini`
3. Going forward:
   - plain `claude` = your original default path
   - `claude-gemini` = LiteLLM + `gemini-3.1-pro-preview`

如果你要把这套结果交给用户，最简单的说法是：

1. 你的原有 Claude/Hermes 配置没有被破坏
2. 新增了一个专用入口：
   - `claude-gemini`
3. 以后：
   - 用普通 `claude` = 走你原来的默认配置
   - 用 `claude-gemini` = 走 LiteLLM + `gemini-3.1-pro-preview`

---

## 12. Minimal execution checklist / 最小执行清单

Do these in order:

1. Confirm LiteLLM is online
2. Verify `/v1/messages`
3. Create the `claude-gemini` wrapper
4. `chmod +x ~/.local/bin/claude-gemini`
5. Run:

```bash
claude-gemini -p "Reply with exactly: ok" --output-format json
```

6. Then use it normally:

```bash
claude-gemini
```

按顺序做这几步就够：

1. 确认 LiteLLM 在线
2. 验证 `/v1/messages`
3. 创建 `claude-gemini` wrapper
4. `chmod +x ~/.local/bin/claude-gemini`
5. 跑：

```bash
claude-gemini -p "Reply with exactly: ok" --output-format json
```

6. 成功后再正式使用：

```bash
claude-gemini
```
