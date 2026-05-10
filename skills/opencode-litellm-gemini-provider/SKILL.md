---
name: opencode-litellm-gemini-provider
description: Add an existing LiteLLM OpenAI-compatible Gemini model to OpenCode as an optional provider without changing the current default model, then optionally make plain `opencode` load LiteLLM credentials so users can switch between OpenAI and Gemini from `/models`.
---

# OpenCode + LiteLLM Gemini Provider

This skill captures a field-tested setup for adding a local LiteLLM-routed Gemini model to OpenCode while preserving the current default model.

本 Skill 沉淀一次真实配置过程：在不改变 OpenCode 当前默认模型的前提下，把本地 LiteLLM 代理暴露的 Gemini 模型加入 OpenCode 模型列表，并可选地让普通 `opencode` 命令自动加载 LiteLLM 凭据，从而在 `/models` 里自由切换 OpenAI 和 Gemini。

---

## When To Use

Use this skill when:
- OpenCode is installed locally and already works with a default model such as `openai/gpt-5.5`
- LiteLLM is already deployed locally and exposes an OpenAI-compatible endpoint
- LiteLLM can call Gemini or Vertex AI models such as `gemini-3.1-pro-preview`
- the user wants to add Gemini as an option, not replace the existing default model
- the user wants plain `opencode` to be the single entrypoint for both OpenAI and LiteLLM-backed models

适用场景：
- 本地已经安装 OpenCode，并且默认模型已经可用，例如 `openai/gpt-5.5`
- 本地已经部署 LiteLLM，并暴露 OpenAI-compatible API
- LiteLLM 已经能调用 Gemini / Vertex AI，例如 `gemini-3.1-pro-preview`
- 用户只想新增一个模型选项，不想改掉当前默认模型
- 用户希望继续只输入 `opencode`，然后在交互式 `/models` 中自由切换 OpenAI 与 Gemini

---

## Mental Model

OpenCode has two separate concerns:
- **Provider/model registration**: what appears in `/models`
- **Runtime credentials**: whether the selected provider can authenticate when a request is sent

The minimal safe integration is:
- add a custom `litellm` provider in `~/.config/opencode/opencode.json`
- use `@ai-sdk/openai-compatible` because LiteLLM exposes an OpenAI-compatible `/v1` API
- define the LiteLLM model ID exactly as LiteLLM returns it from `/v1/models`
- do **not** set the top-level OpenCode `model` field unless the user wants to change the default
- ensure `LITELLM_MASTER_KEY` is present in the `opencode` process environment

核心理解：
- OpenCode 的“模型能不能显示在 `/models`”和“调用时能不能鉴权成功”是两件事
- `opencode.json` 负责把 LiteLLM 注册为 provider，并声明模型
- `LITELLM_MASTER_KEY` 负责让实际请求通过 LiteLLM 鉴权
- 只新增 provider，不写顶层 `model` 字段，就不会改变当前默认模型

---

## Real Working Setup

The setup that produced this skill used:

```text
OpenCode binary: /Users/toby/.opencode/bin/opencode
OpenCode config: /Users/toby/.config/opencode/opencode.json
LiteLLM project: /Users/toby/TobyLab/litellm-vertex-proxy
LiteLLM API base: http://127.0.0.1:4000/v1
LiteLLM model: gemini-3.1-pro-preview
OpenCode model ID: litellm/gemini-3.1-pro-preview
Existing default model: openai/gpt-5.5
```

LiteLLM already exposed:

```text
gemini-3.1-pro-preview -> vertex_ai/gemini-3.1-pro-preview
gemini-pro             -> vertex_ai/gemini-3.1-pro-preview
gemini-2.5-pro         -> vertex_ai/gemini-2.5-pro
gemini-2.5-flash       -> vertex_ai/gemini-2.5-flash
```

真实配置中的关键点：
- LiteLLM 配置与密钥不写入 OpenCode 仓库或聊天输出
- `LITELLM_MASTER_KEY` 从 LiteLLM 项目的 `.env` 读取
- OpenCode 配置里只引用 `{env:LITELLM_MASTER_KEY}`
- 普通 `opencode` 最终被包装为自动加载 LiteLLM 环境后再执行原始二进制

---

## Step 1: Confirm LiteLLM Is Healthy

Before touching OpenCode, confirm the proxy itself works.

For Toby's local proxy:

```bash
cd /Users/toby/TobyLab/litellm-vertex-proxy
./scripts/service.sh status
bash -lc 'source ./scripts/env.sh && ./scripts/list-models.sh'
bash -lc 'source ./scripts/env.sh && ./scripts/test-chat.sh gemini-3.1-pro-preview'
```

Expected model list includes:

```text
gemini-3.1-pro-preview
```

中文说明：先确认 LiteLLM 自己能跑，再接 OpenCode。不要一开始就改 OpenCode，否则排障时会混淆是 LiteLLM 挂了，还是 OpenCode 配置错了。

---

## Step 2: Inspect OpenCode Paths And Current Defaults

Use OpenCode's own debug commands:

```bash
command -v opencode
opencode debug paths
opencode debug config
opencode providers list
opencode models openai
```

Important observation from the real setup:

```json
{
  "agent": {},
  "mode": {},
  "plugin": [],
  "command": {},
  "username": "toby"
}
```

There was no top-level `model` in config, so OpenCode's current default came from its own last-used/internal priority behavior. The integration therefore avoided writing a top-level `model`.

中文说明：如果用户说“不改默认模型”，就不要写：

```json
"model": "litellm/gemini-3.1-pro-preview"
```

只注册 provider 和 models 即可。

---

## Step 3: Add The LiteLLM Provider

Create or update:

```text
~/.config/opencode/opencode.json
```

Reference config:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "litellm": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LiteLLM Vertex Proxy",
      "env": ["LITELLM_MASTER_KEY"],
      "options": {
        "baseURL": "http://127.0.0.1:4000/v1",
        "apiKey": "{env:LITELLM_MASTER_KEY}",
        "timeout": 600000
      },
      "models": {
        "gemini-3.1-pro-preview": {
          "name": "Gemini 3.1 Pro Preview via LiteLLM",
          "family": "gemini",
          "attachment": true,
          "reasoning": true,
          "temperature": true,
          "tool_call": true,
          "limit": {
            "context": 1000000,
            "output": 65536
          },
          "modalities": {
            "input": ["text", "image", "pdf"],
            "output": ["text"]
          }
        }
      }
    }
  }
}
```

Notes:
- `provider.litellm` is the provider ID, so the OpenCode model ID becomes `litellm/gemini-3.1-pro-preview`
- `baseURL` must include `/v1` for the OpenAI-compatible provider
- `apiKey` should come from the environment; do not hardcode secrets
- leaving top-level `model` absent preserves the existing default model

中文要点：
- `litellm` 是 OpenCode 里的 provider 名称，不是 LiteLLM 服务名
- 模型完整选择名是 `litellm/gemini-3.1-pro-preview`
- `baseURL` 用 `http://127.0.0.1:4000/v1`
- 不要把 `LITELLM_MASTER_KEY` 明文写进配置

---

## Step 4: Verify Model Visibility

If `LITELLM_MASTER_KEY` is already in the shell environment:

```bash
opencode models litellm
```

If the key lives in the LiteLLM project `.env`, source the proxy environment first:

```bash
bash -lc 'source /Users/toby/TobyLab/litellm-vertex-proxy/scripts/env.sh && opencode models litellm'
```

Expected output:

```text
litellm/gemini-3.1-pro-preview
```

Also verify OpenAI still works:

```bash
opencode models openai
```

Expected output includes:

```text
openai/gpt-5.5
```

---

## Step 5: Choose The Launch Mode

There are two safe launch patterns.

### Mode A: Parallel Wrapper

Use this when the user wants a low-risk extra command and does not require plain `opencode` to load LiteLLM credentials.

Example:

```text
~/.local/bin/opencode-litellm
```

Wrapper:

```bash
#!/usr/bin/env bash
set -euo pipefail

source /Users/toby/TobyLab/litellm-vertex-proxy/scripts/env.sh
exec opencode "$@"
```

Then:

```bash
chmod 700 ~/.local/bin/opencode-litellm
opencode-litellm models litellm
opencode-litellm
```

Inside TUI:

```text
/models
```

The user should see both:

```text
openai/gpt-5.5
litellm/gemini-3.1-pro-preview
```

### Mode B: Make Plain `opencode` Load LiteLLM Credentials

Use this only when the user explicitly asks to keep using the same `opencode` command.

The real setup did this:

```bash
mv /Users/toby/.opencode/bin/opencode /Users/toby/.opencode/bin/opencode.real
```

Then created a new wrapper at:

```text
/Users/toby/.opencode/bin/opencode
```

Wrapper:

```bash
#!/usr/bin/env bash
set -euo pipefail

source /Users/toby/TobyLab/litellm-vertex-proxy/scripts/env.sh
exec /Users/toby/.opencode/bin/opencode.real "$@"
```

Then:

```bash
chmod 755 /Users/toby/.opencode/bin/opencode
opencode models litellm
opencode models openai
```

中文说明：
- Mode A 风险更低，新增 `opencode-litellm`
- Mode B 用户体验最好，继续输入 `opencode`
- Mode B 会移动原始二进制，因此必须保留 `opencode.real` 作为回滚点
- 如果 OpenCode 升级器覆盖了二进制，可能需要重新应用 wrapper

---

## Step 6: Interactive Switching

After Mode A or Mode B is in place, launch OpenCode:

```bash
opencode
```

Then in the TUI:

```text
/models
```

Switch freely between:

```text
openai/gpt-5.5
litellm/gemini-3.1-pro-preview
```

The selected model applies to the current OpenCode session. Run `/models` again to switch back.

中文说明：配置完成后，用户无需改默认模型。进入 OpenCode 后通过 `/models` 手动选择。切到 Gemini 后请求走 LiteLLM；再打开 `/models` 可以切回 GPT-5.5。

---

## Smoke Tests

Useful checks:

```bash
opencode debug config
opencode models litellm
opencode models openai
opencode run -m litellm/gemini-3.1-pro-preview "只回答 OK"
```

If the run command prints the model header and does not fail authentication, the OpenCode-to-LiteLLM path is wired.

If `opencode debug config` shows:

```json
"apiKey": ""
```

then the shell running `opencode debug config` did not have `LITELLM_MASTER_KEY`. This does not necessarily mean the config is wrong; it means the runtime environment did not load the key. Use the wrapper or source the LiteLLM env script.

中文排障：如果 `apiKey` 为空，优先检查是不是直接运行了普通二进制，或者 wrapper 没有加载 LiteLLM 项目的 `scripts/env.sh`。

---

## Rollback

For Mode A:

```bash
rm ~/.local/bin/opencode-litellm
```

For Mode B:

```bash
mv /Users/toby/.opencode/bin/opencode.real /Users/toby/.opencode/bin/opencode
```

To remove the model option entirely, remove the `provider.litellm` block from:

```text
~/.config/opencode/opencode.json
```

中文回滚：
- 只加 wrapper 的模式，删掉 wrapper 即可
- 替换普通 `opencode` 的模式，把 `opencode.real` 移回 `opencode`
- 如果完全不要 LiteLLM 选项，删除 `opencode.json` 中的 `provider.litellm`

---

## Common Pitfalls

- Do not set top-level `model` unless the user explicitly wants to change the default.
- Do not hardcode `LITELLM_MASTER_KEY` in `opencode.json`.
- For OpenAI-compatible providers, use `/v1` in `baseURL`.
- Confirm the LiteLLM model ID with `/v1/models`; do not guess the model name.
- If using zsh, source Bash-oriented scripts through `bash -lc` when they rely on `BASH_SOURCE`.
- Wrapping the main `opencode` binary can be overwritten by future OpenCode upgrades.
- Keep a clear rollback path before moving the original binary.

常见坑：
- 写了顶层 `model`，导致默认模型被改掉
- 把 master key 明文写进配置或提交到仓库
- `baseURL` 少了 `/v1`
- LiteLLM 真实模型 ID 和 OpenCode 配置里的模型 ID 不一致
- zsh 直接 source 依赖 `BASH_SOURCE` 的 Bash 脚本会失败
- OpenCode 升级后可能覆盖 wrapper，需要重新检查

---

## Final User-Facing Summary Template

English:

```text
OpenCode now has a LiteLLM provider at `litellm/gemini-3.1-pro-preview` while preserving the existing default model. Start OpenCode with `opencode`, run `/models`, and switch between `openai/gpt-5.5` and `litellm/gemini-3.1-pro-preview` as needed.
```

中文：

```text
已经在不改变默认模型的前提下，为 OpenCode 新增 `litellm/gemini-3.1-pro-preview`。以后直接运行 `opencode`，进入后用 `/models` 即可在 `openai/gpt-5.5` 和 Gemini 之间切换。
```
