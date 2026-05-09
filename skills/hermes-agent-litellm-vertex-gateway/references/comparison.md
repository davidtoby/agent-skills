# Comparison — Hermes vs OpenClaw vs Claude Code

同一套 LiteLLM Vertex Proxy，在不同 Agent 系统里的接入方式对比。

---

## Hermes Agent

**配置位置：** `~/.hermes/config.yaml`

**Provider 配置方式：**
```yaml
model:
  default: gpt-5.4
  provider: openai-codex

providers:
  local-litellm:
    name: local-litellm
    base_url: http://127.0.0.1:4000
    api_key: <LITELLM_MASTER_KEY>
    models:
      - gemini-3.1-pro-preview
```

**运行时切换：**
```
/model local-litellm/gemini-3.1-pro-preview
/model openai-codex/gpt-5.4  # 切回
```

**重启要求：** 必须重启 Hermes Gateway 进程

**特点：**
- 配置在 yaml 文件里
- 不支持热更新
- 默认值保持不变，灵活性高

---

## OpenClaw

**配置位置：** `openclaw models` CLI 或 `~/.openclaw/config.yaml`

**Provider 配置方式：**
```yaml
models:
  providers:
    litellm-vertex:
      name: litellm-vertex
      api_key: <LITELLM_MASTER_KEY>
      base_url: http://127.0.0.1:4000/v1

agents:
  defaults:
    models:
      - id: litellm-vertex/gemini-3.1-pro-preview
        alias: GeminiVertex
```

**运行时切换：**
```bash
openclaw models set GeminiVertex
openclaw agent --local --model litellm-vertex/gemini-3.1-pro-preview --message "..."
```

**重启要求：** 配置 hot-reload，部分变更需要 gateway 重启

---

## Claude Code

**配置位置：** 环境变量

**方式 A — Wrapper 脚本（不修改原有 claude 配置）：**
```bash
# claude-gemini-wrapper.sh
export ANTHROPIC_BASE_URL=http://127.0.0.1:4000
export ANTHROPIC_AUTH_TOKEN=<LITELLM_MASTER_KEY>
export ANTHROPIC_MODEL=gemini-3.1-pro-preview
claude "$@"
```

**方式 B — 直接改环境变量（改动较大）：**
```bash
export ANTHROPIC_BASE_URL=http://127.0.0.1:4000
export ANTHROPIC_AUTH_TOKEN=<LITELLM_MASTER_KEY>
export ANTHROPIC_MODEL=gemini-3.1-pro-preview
```

> 注意：`ANTHROPIC_BASE_URL` 必须指向 LiteLLM 根，不能带 `/v1`

---

## 快速对照表

| 属性 | Hermes | OpenClaw | Claude Code |
|---|---|---|---|
| 配置位置 | `~/.hermes/config.yaml` | `openclaw models` / config | 环境变量 |
| 临时切换命令 | `/model provider/model` | `openclaw models set` | wrapper 脚本 |
| 永久切默认 | 修改 `model.provider` | `openclaw models set` | 修改环境变量 |
| 热更新 | ❌ | ✅ 部分 | ❌ |
| 切换粒度 | provider/model | provider/model/alias | 全局环境变量 |
