# Claude Code + LiteLLM 中文快速开始

这份 quickstart 面向已经满足以下前提的场景：

- 你已经安装好了 Claude Code
- 你本机已经有一个可用的 LiteLLM
- LiteLLM 已经能代理到目标模型
- 你**不想破坏**已有的 Hermes / OpenClaw / Claude 其它配置

Toby 这次的成功案例是：

- Claude Code
- 通过 LiteLLM
- 调用 Vertex AI 后端的
- `gemini-3.1-pro-preview`

本机 LiteLLM 路径：

```text
/Users/toby/TobyLab/litellm-vertex-proxy
```

本机 LiteLLM 地址：

```text
http://127.0.0.1:4000
```

目标模型：

```text
gemini-3.1-pro-preview
```

---

## 一、先理解核心思路

不要把这件事理解成“让 Claude Code 原生支持 Gemini 名字”。

正确理解是：

1. Claude Code 仍然按 **Anthropic 风格** 发请求
2. 它把请求发给 LiteLLM
3. LiteLLM 再把请求翻译并路由到真正的上游模型
4. 这里真正的上游模型是：
   - `vertex_ai/gemini-3.1-pro-preview`

所以 Claude Code 这一侧重点不是改模型能力，而是：

- 配对 `ANTHROPIC_BASE_URL`
- 配对 `ANTHROPIC_AUTH_TOKEN`
- 配对 `ANTHROPIC_MODEL`

---

## 二、先确认 LiteLLM 本身是好的

先不要急着跑 Claude Code。

先确认 LiteLLM 服务本身没问题：

```bash
cd /Users/toby/TobyLab/litellm-vertex-proxy
./scripts/service.sh status
lsof -nP -iTCP:4000 -sTCP:LISTEN
```

如果 `127.0.0.1:4000` 没监听，就先修 LiteLLM，不要往 Claude Code 身上找原因。

---

## 三、一定要验证 `/v1/messages`，不要只看 `/v1/models`

这是一个很关键的坑。

很多人只验证：

```bash
/v1/models
```

但 Claude Code 真正更关键的是 Anthropic 风格的：

```bash
/v1/messages
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

成功时你应该看到类似：

```json
{"type":"message","model":"gemini-3.1-pro-preview","content":[{"type":"text","text":"ok"}]}
```

这一步成功，才说明 Claude Code 走 LiteLLM 的基础链路是通的。

---

## 四、为什么不能直接硬上 `claude`

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

这会导致几个问题：

- 你以为在测 LiteLLM，其实没走 LiteLLM
- `--model gemini-3.1-pro-preview` 可能被本地校验或 provider 路径拦住
- 你为了修 Claude Code，反而把原来能用的全局配置搞乱

所以这次成功经验的关键决策是：

**不要粗暴改全局 `claude`，而是新增一个单独入口。**

---

## 五、推荐做法：新增 `claude-gemini` wrapper

推荐新建：

```text
~/.local/bin/claude-gemini
```

参考脚本：

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

然后给它执行权限：

```bash
chmod +x ~/.local/bin/claude-gemini
```

可选：加一个 alias

```bash
alias cgemini="claude-gemini"
```

---

## 六、几个最关键的参数解释

### 1) `ANTHROPIC_BASE_URL`
必须是：

```bash
http://127.0.0.1:4000
```

**不要写成：**

```bash
http://127.0.0.1:4000/v1
```

因为 Claude Code 会自己访问 `/v1/messages`。

### 2) `ANTHROPIC_AUTH_TOKEN`
这里应该用 LiteLLM 的 master key：

```bash
$LITELLM_MASTER_KEY
```

### 3) `ANTHROPIC_MODEL`
这里直接写 LiteLLM 暴露出来的模型名：

```bash
gemini-3.1-pro-preview
```

### 4) `--setting-sources project,local`
这一步非常重要。

它的作用是：

- 本次启动时，不加载 user 级设置来源
- 避免 `~/.claude/settings.json` 里的旧配置抢路由

### 5) `unset CLAUDE_CODE_USE_VERTEX`
这一步是为了防止 Claude Code 继续按你旧的 Vertex 直连链路走。

---

## 七、先用 print mode 验证

不要上来就交互式。

先跑一个最小验证：

```bash
claude-gemini -p "Reply with exactly: wrapper-ok" --output-format json
```

如果成功，你应该看到：

- `subtype: success`
- 返回文本是 `wrapper-ok`
- 输出里的 `modelUsage` 指向：
  - `gemini-3.1-pro-preview`

这一步是最小可证据链。

---

## 八、确认成功后再正式用

### 交互式

```bash
claude-gemini
```

### 单次命令

```bash
claude-gemini -p "帮我总结这个仓库" --output-format json
```

### 如果你配了 alias

```bash
cgemini
```

---

## 九、这套方案为什么安全

因为它遵循的是“并行接入，不破坏现状”：

- `claude` 继续保留原来的行为
- `claude-gemini` 专门走 LiteLLM + Gemini
- Hermes Agent 原来的 LiteLLM 调用链完全不动

这比直接去覆盖 `~/.claude/settings.json` 安全得多。

---

## 十、最常见的坑

### 坑 1：把 `ANTHROPIC_BASE_URL` 写成 `/v1`
错。

应该是根地址：

```bash
http://127.0.0.1:4000
```

### 坑 2：只测 `/v1/models`
不够。

还要测：

```bash
/v1/messages
```

### 坑 3：直接修改全局 `claude` 配置
风险很高。

优先用独立 wrapper。

### 坑 4：忘记 `--setting-sources project,local`
会导致 `~/.claude/settings.json` 抢路由。

### 坑 5：LiteLLM 没起来就怪 Claude Code
先检查：

```bash
./scripts/service.sh status
lsof -nP -iTCP:4000 -sTCP:LISTEN
```

---

## 十一、推荐给最终用户的话术

如果你要把这套结果交给用户，最简单的说法是：

1. 你的原有 Claude/Hermes 配置没有被破坏
2. 新增了一个专用入口：
   - `claude-gemini`
3. 以后：
   - 用普通 `claude` = 走你原来的默认配置
   - 用 `claude-gemini` = 走 LiteLLM + `gemini-3.1-pro-preview`

---

## 十二、最小执行清单

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
