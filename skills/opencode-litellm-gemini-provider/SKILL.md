---
name: opencode-litellm-gemini-provider
description: Configure official native OpenCode to add a local LiteLLM OpenAI-compatible Gemini model as a selectable provider using config-file secret references, without wrappers and without changing the current default model.
---

# OpenCode + LiteLLM Gemini Provider

This skill captures the final, upgrade-friendly way to add a local LiteLLM-routed Gemini model to official OpenCode.

本 Skill 沉淀的是最终采用的、对 OpenCode 官方升级更友好的方案：不改 OpenCode 官方二进制，不使用 wrapper，只通过 OpenCode 原生配置文件把本地 LiteLLM 模型加入 `/models`，并保持现有默认模型不变。

---

## Best Current Approach

Use the official OpenCode binary directly:

```text
~/.opencode/bin/opencode
```

Configure LiteLLM as a custom OpenAI-compatible provider in:

```text
~/.config/opencode/opencode.json
```

Store the LiteLLM master key in a local file with `0600` permissions and reference it from OpenCode config using OpenCode's native `{file:...}` substitution.

核心方案：
- `opencode` 直接命中官方二进制
- 不把 `~/.opencode/bin/opencode` 改成 wrapper
- 不依赖 shell 启动时 export `LITELLM_MASTER_KEY`
- 不修改顶层 `model` 字段，因此不改变当前默认模型
- 使用 `{file:/path/to/key}` 让 OpenCode 自己读取本地密钥文件

---

## When To Use

Use this skill when:
- OpenCode is installed locally and already works with a model such as `openai/gpt-5.5`
- the user wants to keep official native OpenCode behavior and future `opencode upgrade` compatibility
- LiteLLM is already deployed locally and exposes an OpenAI-compatible endpoint
- LiteLLM can call Gemini or Vertex AI models such as `gemini-3.1-pro-preview`
- the user wants Gemini as an additional selectable model, not as a forced default
- the user wants `/models` to show both ChatGPT/OpenAI models and local LiteLLM models

适用场景：
- 本地已经安装 OpenCode，并且 `openai/gpt-5.5` 等模型已经可用
- 用户希望尽量使用 OpenCode 官方原生能力，不想用 wrapper 包一层
- 本地已经部署 LiteLLM，且提供 OpenAI-compatible `/v1` API
- LiteLLM 已经能调用 Gemini / Vertex AI，例如 `gemini-3.1-pro-preview`
- 用户只想新增一个模型选项，而不是替换当前默认模型
- 用户希望在 OpenCode TUI 的 `/models` 中自由切换 OpenAI 与 LiteLLM Gemini

---

## Mental Model

OpenCode separates three concerns:

- **Program binary**: the executable that provides official OpenCode features
- **Provider/model registration**: the config that determines what appears in `/models`
- **Runtime credentials**: the API key used when a selected provider sends a request

The safest setup keeps those concerns separate:

- official binary remains at `~/.opencode/bin/opencode`
- provider config lives at `~/.config/opencode/opencode.json`
- LiteLLM key lives in a separate private file
- config references that private file with `{file:...}`
- no wrapper is needed

核心理解：
- `~/.opencode/` 是 OpenCode 程序本体/二进制相关目录
- `~/.config/opencode/` 是 OpenCode 用户配置目录
- 想让模型出现在 `/models`，改配置即可，不需要改二进制
- 想让 LiteLLM 鉴权成功，配置里的 `apiKey` 必须能读到 key
- `{file:...}` 比 wrapper 注入环境变量更适合长期维护

---

## Why Not Wrapper As The Primary Solution

Earlier attempts used a wrapper named `opencode` to source LiteLLM environment variables before executing the real binary. It worked, but it introduced operational risk:

- a wrapper can be shadowed or bypassed by PATH order
- a new terminal may hit the official binary instead of the wrapper
- `opencode upgrade` can overwrite installation-managed files if the wrapper replaces the official binary
- future troubleshooting becomes confusing because `opencode` may not be the real executable

The final solution avoids these issues by keeping official OpenCode untouched.

为什么最终不用 wrapper 作为主方案：
- PATH 顺序一变，新窗口可能绕过 wrapper
- wrapper 如果放在 `~/.opencode/bin/opencode`，会占用官方安装器管理的路径
- 升级时可能被覆盖，或者让升级排障变复杂
- 原生配置方式更清晰：二进制归 OpenCode 管，模型与密钥归配置管

---

## Real Working Setup

The real machine setup that produced this skill:

```text
Official OpenCode binary: /Users/toby/.opencode/bin/opencode
OpenCode config:          /Users/toby/.config/opencode/opencode.json
LiteLLM project:          /Users/toby/TobyLab/litellm-vertex-proxy
LiteLLM API base:         http://127.0.0.1:4000/v1
LiteLLM key file:         /Users/toby/TobyLab/litellm-vertex-proxy/.opencode-litellm-key
LiteLLM model:            gemini-3.1-pro-preview
OpenCode model ID:        litellm/gemini-3.1-pro-preview
Existing OpenAI model:    openai/gpt-5.5
```

LiteLLM already exposed:

```text
gemini-3.1-pro-preview -> vertex_ai/gemini-3.1-pro-preview
gemini-pro             -> vertex_ai/gemini-3.1-pro-preview
gemini-2.5-pro         -> vertex_ai/gemini-2.5-pro
gemini-2.5-flash       -> vertex_ai/gemini-2.5-flash
```

Final verification showed:

```text
command -v opencode
=> /Users/toby/.opencode/bin/opencode

opencode models litellm
=> litellm/gemini-3.1-pro-preview

opencode models openai
=> openai/gpt-5.5
```

---

## Step 1: Confirm LiteLLM Works First

Before changing OpenCode, verify the LiteLLM proxy itself.

Example for Toby's local proxy:

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

中文说明：先确认 LiteLLM 自己健康，再接 OpenCode。否则后续 `Authentication Error` 或 model not found 很难判断是 LiteLLM 的问题还是 OpenCode 配置的问题。

---

## Step 2: Confirm Official OpenCode Is Being Used

Check path resolution:

```bash
command -v opencode
type opencode
file /Users/toby/.opencode/bin/opencode
```

Desired result:

```text
/Users/toby/.opencode/bin/opencode
/Users/toby/.opencode/bin/opencode: Mach-O 64-bit executable arm64
```

If `command -v opencode` points to a wrapper such as `~/.local/bin/opencode`, disable or rename that wrapper.

Real cleanup command used:

```bash
mv /Users/toby/.local/bin/opencode /Users/toby/.local/bin/opencode.wrapper.backup
```

Then make shell PATH prefer the official OpenCode directory if needed:

```bash
export PATH="/Users/toby/.opencode/bin:$HOME/.local/bin:$PATH"
```

真实排障：之前新窗口报 `Authentication Error, No api key passed in`，根因是 PATH 命中了错误的入口或没有加载 key。最终方案不再需要 wrapper，所以应确保 `opencode` 是官方二进制。

---

## Step 3: Create A Private Key File For OpenCode

OpenCode supports native file substitution:

```text
{file:/absolute/path/to/secret}
```

Create a key file that contains only the LiteLLM master key.

Example:

```bash
bash -lc 'set -euo pipefail; source /Users/toby/TobyLab/litellm-vertex-proxy/scripts/env.sh; umask 077; printf "%s" "$LITELLM_MASTER_KEY" > /Users/toby/TobyLab/litellm-vertex-proxy/.opencode-litellm-key; chmod 600 /Users/toby/TobyLab/litellm-vertex-proxy/.opencode-litellm-key; test -s /Users/toby/TobyLab/litellm-vertex-proxy/.opencode-litellm-key'
```

Verify permissions without printing the secret:

```bash
ls -l /Users/toby/TobyLab/litellm-vertex-proxy/.opencode-litellm-key
```

Expected shape:

```text
-rw------- ... .opencode-litellm-key
```

中文说明：
- 这个文件只放 LiteLLM master key
- 不要把 key 打印到聊天、日志、README、commit 或截图里
- 权限用 `600`
- 如果 LiteLLM master key 以后变更，需要同步更新这个文件

---

## Step 4: Configure The LiteLLM Provider In OpenCode

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
      "options": {
        "baseURL": "http://127.0.0.1:4000/v1",
        "apiKey": "{file:/Users/toby/TobyLab/litellm-vertex-proxy/.opencode-litellm-key}",
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

Important details:
- `provider.litellm` is the provider ID
- the selectable OpenCode model becomes `litellm/gemini-3.1-pro-preview`
- `npm` should be `@ai-sdk/openai-compatible` for LiteLLM's OpenAI-compatible API
- `baseURL` should include `/v1`
- `apiKey` uses `{file:...}`, not `{env:...}`
- do not set top-level `model` unless the user explicitly wants to change the default

中文要点：
- `litellm` 是 OpenCode 中的 provider ID
- 最终在 `/models` 里看到的是 `litellm/gemini-3.1-pro-preview`
- `baseURL` 是 `http://127.0.0.1:4000/v1`
- `apiKey` 通过 `{file:...}` 读取本地密钥文件
- 不写顶层 `model`，就不会把默认模型从 `openai/gpt-5.5` 改成 Gemini

---

## Step 5: Verify Both Providers

Run from a fresh shell:

```bash
command -v opencode
opencode debug config
opencode models litellm
opencode models openai
```

Expected:

```text
command -v opencode
=> /Users/toby/.opencode/bin/opencode

opencode models litellm
=> litellm/gemini-3.1-pro-preview

opencode models openai
=> openai/gpt-5.5
```

Optional smoke test:

```bash
opencode run -m litellm/gemini-3.1-pro-preview "只回答 OK"
```

If `opencode debug config` shows the actual key value, avoid pasting that output into public logs or commits. The key should still not be stored in the config file itself.

中文说明：验证重点是三件事：
- `opencode` 是官方二进制
- `litellm/gemini-3.1-pro-preview` 能出现在模型列表里
- `openai/gpt-5.5` 仍然可见，说明没有破坏原有 OpenAI 模型

---

## Step 6: Use In TUI

Launch OpenCode normally:

```bash
opencode
```

Inside the TUI:

```text
/models
```

Switch between:

```text
openai/gpt-5.5
litellm/gemini-3.1-pro-preview
```

The selected model applies to the current OpenCode session. Use `/models` again to switch back.

中文说明：以后就是原生 OpenCode 用法。直接输入 `opencode`，在 TUI 里用 `/models` 选择模型。切换到 Gemini 时走本地 LiteLLM；切回 GPT-5.5 时走 OpenAI。

---

## Upgrade Behavior

This approach is upgrade-friendly because it does not replace or wrap the official binary.

Future command:

```bash
opencode upgrade
```

can update:

```text
~/.opencode/bin/opencode
```

The provider config remains in:

```text
~/.config/opencode/opencode.json
```

So new OpenCode features should remain available through the official binary, and the LiteLLM provider should keep working as long as OpenCode continues supporting custom providers and `{file:...}` config substitution.

升级影响：
- 官方二进制仍然归 OpenCode 管理
- `opencode upgrade` 更新官方二进制，不会覆盖你的 provider 配置
- 新版 OpenCode 的官方功能仍然通过原生二进制获得
- 只要 OpenCode 继续支持自定义 provider 与 `{file:...}`，这个配置就能延续

---

## Rollback

To remove the LiteLLM model option:

```text
Remove provider.litellm from ~/.config/opencode/opencode.json
```

To remove the private key file:

```bash
rm /Users/toby/TobyLab/litellm-vertex-proxy/.opencode-litellm-key
```

To restore a previously disabled wrapper, only if needed:

```bash
mv /Users/toby/.local/bin/opencode.wrapper.backup /Users/toby/.local/bin/opencode
```

中文回滚：
- 删除 `opencode.json` 里的 `provider.litellm` 即可让模型从 `/models` 消失
- 删除 `.opencode-litellm-key` 即可移除给 OpenCode 用的 LiteLLM key 文件
- 不需要恢复或改动官方 OpenCode 二进制

---

## Common Pitfalls

- Do not hardcode the LiteLLM key in `opencode.json`.
- Do not commit `.opencode-litellm-key` or any `.env` file containing secrets.
- Do not set top-level `model` if the user wants to preserve the default model.
- Use `/v1` in `baseURL` for the OpenAI-compatible provider.
- Confirm the model ID with LiteLLM's `/v1/models`; do not guess it.
- If `Authentication Error, No api key passed in` appears, inspect `opencode debug config` and confirm `apiKey` resolves through `{file:...}`.
- If `command -v opencode` points to `~/.local/bin/opencode`, a wrapper may still be shadowing the official binary.
- If zsh PATH puts `~/.local/bin` before `~/.opencode/bin`, ensure there is no stale `~/.local/bin/opencode` wrapper.

常见坑：
- 把 master key 明文写进 `opencode.json`
- 把 key 文件或 `.env` 提交到 GitHub
- 写了顶层 `model`，导致默认模型被改成 Gemini
- `baseURL` 少了 `/v1`
- 模型名和 LiteLLM 暴露的模型名不一致
- 旧 wrapper 仍然在 PATH 前面，导致以为自己在用官方二进制，实际不是

---

## Historical Alternative: Wrapper Mode

Wrapper mode can still work, but it is no longer the recommended primary solution for OpenCode.

It looked like this:

```bash
#!/usr/bin/env bash
set -euo pipefail

source /Users/toby/TobyLab/litellm-vertex-proxy/scripts/env.sh
exec /Users/toby/.opencode/bin/opencode "$@"
```

Use wrapper mode only when:
- the runtime cannot use `{file:...}`
- the user explicitly wants environment-variable injection
- the wrapper has a distinct name such as `opencode-litellm`, not a replacement for official `opencode`

历史经验：wrapper 可以工作，但它不是最稳的长期方案。优先使用官方二进制 + `opencode.json` + `{file:...}`。

---

## Final User-Facing Summary Template

English:

```text
OpenCode now uses the official native binary directly. The LiteLLM Gemini model is configured as `litellm/gemini-3.1-pro-preview` through `~/.config/opencode/opencode.json`, with the API key loaded via OpenCode's `{file:...}` secret reference. Start OpenCode with `opencode`, run `/models`, and switch between `openai/gpt-5.5` and `litellm/gemini-3.1-pro-preview`.
```

中文：

```text
现在使用的是官方原生 OpenCode 二进制，没有 wrapper。LiteLLM Gemini 模型通过 `~/.config/opencode/opencode.json` 配置为 `litellm/gemini-3.1-pro-preview`，API key 由 OpenCode 原生 `{file:...}` 读取。以后直接运行 `opencode`，进入后用 `/models` 在 `openai/gpt-5.5` 和 Gemini 之间切换。
```
