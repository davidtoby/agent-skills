# Troubleshooting — Hermes + LiteLLM Vertex Proxy

## 症状：401 Authentication Error

**表现：**
```
{"error":{"message":"Authentication Error, No api key passed in.","type":"auth_error","param":"None","code":"401"}}
```

**原因：** `config.yaml` 中 `providers.local-litellm.api_key` 为空或错误

**排查步骤：**
1. 从 `~/GitHub-Codebase/litellm-vertex-proxy/.env` 读取真实的 `LITELLM_MASTER_KEY`
2. 确认 `config.yaml` 中 `api_key: <实际key>` 已填写
3. 重启 Hermes 后重试

---

## 症状：model not found

**表现：** Hermes 响应说模型不存在

**排查步骤：**
```bash
curl -s -H "Authorization: Bearer <KEY>" http://127.0.0.1:4000/v1/models \
  | python3 -c "import sys,json; d=json.load(sys.stdin); [print(m['id']) for m in d.get('data',[])]"
```

确认实际模型 ID，修改 `config.yaml` 中 `models` 列表

---

## 症状：Proxy 正常，但 Hermes 无法连接

**排查：**
1. 确认端口监听：`lsof -nP -iTCP:4000 -sTCP:LISTEN`
2. 确认 localhost 访问：`curl -s http://127.0.0.1:4000/openapi.json`
3. 检查防火墙：`sudo pfctl -sr | grep 4000`（如有必要）

---

## 症状：Hermes 重启后配置还原

**原因：** 可能存在 config 自动覆写机制

**对策：**
1. 确认备份已保存
2. 如有必要，把配置写入独立文件并在启动脚本中注入
