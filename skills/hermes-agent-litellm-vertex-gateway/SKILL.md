---
name: hermes-agent-litellm-vertex-gateway
description: Configure an existing Hermes Agent deployment to use a local LiteLLM Vertex Proxy as an additional model option, without disturbing the current Hermes configuration. Use when you need Hermes to access Gemini models via a local LiteLLM gateway already running at 127.0.0.1:4000.
---

# Hermes Agent — Connect to Local LiteLLM Vertex Proxy

让 Hermes Agent 连接到本地已有的 LiteLLM Vertex Proxy，以使用 Gemini 模型，不影响现有配置。

## Situation

本地已部署 LiteLLM Vertex Proxy（`http://127.0.0.1:4000`），现在需要让 Hermes Agent 在不更改当前配置的情况下，多一个调用本地 Gemini 的选项，并支持临时切换。

---

## Prerequisites

1. LiteLLM Vertex Proxy 已运行在 `127.0.0.1:4000`
2. Proxy 已配置 `LITELLM_MASTER_KEY`
3. 至少一个 Gemini 模型已暴露（通过 `GET /v1/models` 可验证）
4. Hermes Agent 已安装并运行在 `~/.hermes/`

---

## Step 1 — Verify the LiteLLM Proxy

在配置 Hermes 之前，先验证 proxy 可用：

```bash
# 1. 检查端口监听
lsof -nP -iTCP:4000 -sTCP:LISTEN

# 2. 获取 master key（从 proxy 项目目录的 .env）
grep LITELLM_MASTER_KEY ~/GitHub-Codebase/litellm-vertex-proxy/.env

# 3. 验证 /v1/models 可访问
curl -s -H "Authorization: Bearer <LITELLM_MASTER_KEY>" http://127.0.0.1:4000/v1/models

# 4. 确认可用模型名
curl -s -H "Authorization: Bearer <LITELLM_MASTER_KEY>" http://127.0.0.1:4000/v1/models \
  | python3 -c "import sys,json; d=json.load(sys.stdin); [print(m['id']) for m in d.get('data',[])]"
```

输出类似：
```
gemini-3.1-pro-preview
```

---

## Step 2 — Locate Hermes Config

```
~/.hermes/config.yaml
```

---

## Step 3 — Add the Provider and Model to config.yaml

```bash
# 备份
cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak.$(date +%Y%m%d%H%M%S)
```

编辑 `~/.hermes/config.yaml`，替换顶部的 `model:` 和 `providers:` 块：

```yaml
model:
  default: gpt-5.4              # 保持原有默认不变
  provider: openai-codex        # 保持原有默认不变
  base_url: https://chatgpt.com/backend-api/codex

providers:
  local-litellm:
    name: local-litellm
    base_url: http://127.0.0.1:4000
    api_key: <LITELLM_MASTER_KEY>
    models:
      - gemini-3.1-pro-preview
```

> ⚠️ `<LITELLM_MASTER_KEY>` 替换为实际值，从 `~/GitHub-Codebase/litellm-vertex-proxy/.env` 中读取。
> 不要把这个 key 打印到聊天里。

---

## Step 4 — Restart Hermes Gateway

```bash
# 方式 A：如果是 Hermes Agent 运行在终端
# 按 Ctrl+C 停止，然后重新启动

# 方式 B：如果是通过 launchd/systemd 运行
# 查找并重启对应服务
launchctl list | grep hermes
# 或
ps aux | grep hermes
```

---

## Step 5 — Verify the Connection

```bash
# 在 Hermes 对话中发送：
/model local-litellm/gemini-3.1-pro-preview
```

应该能正常响应。如果报错，检查：
1. `LITELLM_MASTER_KEY` 是否正确
2. proxy 是否仍在 4000 端口监听

---

## Switching Models

| 操作 | 命令 |
|---|---|
| 切到本地 Gemini | `/model local-litellm/gemini-3.1-pro-preview` |
| 切回原有默认 | `/model openai-codex/gpt-5.4` |
| 查看当前模型 | `/status` |
| 查看所有可用模型 | `/models` |

---

## Rollback

```bash
# 恢复备份
cp ~/.hermes/config.yaml.bak.<timestamp> ~/.hermes/config.yaml
```

---

## Key Differences from OpenClaw / Claude Code Integration

| 系统 | 配置位置 | 切换方式 |
|---|---|---|
| **Hermes Agent** | `~/.hermes/config.yaml` 的 `providers` | `/model <provider>/<model>` |
| **OpenClaw** | `openclaw models set` 或配置文件 | `/model local-litellm/gemini-3.1-pro-preview` |
| **Claude Code** | 环境变量 `ANTHROPIC_BASE_URL` 等 | wrapper 脚本 |

---

## Common Issues

### 401 Authentication Error
- proxy 需要 Bearer token，确认 `api_key` 在 `config.yaml` 的 `providers.local-litellm` 下配置正确

### Model not found
- 确认 `/v1/models` 返回的模型 ID 与配置中 `models` 列表一致

### Hermes 重启后配置丢失
- Hermes Agent 不支持热更新，必须重启进程

---

## Files in this Skill

- `references/troubleshooting.md` — 常见错误速查
- `references/comparison.md` — 与 OpenClaw / Claude Code 集成方案的对比
