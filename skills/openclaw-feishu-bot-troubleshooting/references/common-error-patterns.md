# Common Error Patterns — OpenClaw Feishu Channel

## Error → Cause → Fix quick reference

### `Cannot find package '@larksuiteoapi/node-sdk'`
- **Cause**: Agent tries to send Feishu message but the SDK package is not installed in the global openclaw node_modules
- **Fix**: `cd /usr/lib/node_modules/openclaw && npm install @larksuiteoapi/node-sdk`
- **Prevention**: Ensure post-install hooks run after OpenClaw updates

### `Outbound not configured for channel: feishu`
- **Cause**: The `openclaw-lark` plugin is disabled or not loaded. Agent generates a reply but has no outbound channel to send it.
- **Fix**: `openclaw config set plugins.entries.openclaw-lark.enabled true` then restart Gateway
- **Verify**: `openclaw plugins list | grep lark` should show enabled

### `pairing request sender=...`
- **Cause**: `dmPolicy: pairing` is set but the sender has not been approved on this instance
- **Fix**: `openclaw pairing approve feishu <CODE>` or change `dmPolicy` to `open`
- **Context**: Common after migrating OpenClaw to a new server — pairing state is instance-bound

### `liveness warning: eventLoopDelayP99Ms=...`
- **Cause**: Event loop is blocked, usually by a slow agent prep phase
- **Fix**: Clean session bloat (see `scripts/clean-session-bloat.sh`)
- **If repeated**: Check for infinite loops in custom skills or excessively large context windows

### `stuck session: ... age=...s, stuck for ...s`
- **Cause**: An agent session is hung, usually because Gateway restarted while the agent was processing
- **Fix**: Let the recovery system handle it, or kill and restart Gateway if it persists
- **Prevention**: Do not restart Gateway repeatedly during active message processing

### `abort signal received, stopping`
- **Cause**: Gateway received SIGUSR1 (config hot reload) or was killed by external process
- **Fix**: Check if supervisord/cron is conflicting with manual startup. Use only one startup method.
- **Prevention**: Ensure only one Gateway process runs per app_id

### `WebSocket client ready` but no messages
- **Cause**: WebSocket is connected, but Feishu platform is not sending events
- **Fix**: Check Feishu developer console → Event subscription → confirm `im.message.receive_v1` is added and mode is "long connection"
- **Verify**: Use tenant_access_token API test to confirm app credentials are valid

### `dispatch complete (queuedFinal=true, replies=1)` but user sees nothing
- **Cause**: Agent generated a reply, but the reply was not successfully sent
- **Checklist**:
  1. Is `openclaw-lark` plugin enabled?
  2. Is `@larksuiteoapi/node-sdk` installed?
  3. Any `message failed` or `HTTP 400` errors after dispatch complete?
  4. Is the session stuck (check `stuck session` logs)?

### Agent prep takes >60s
- **Cause**: Session history files are too large
- **Fix**: Run `scripts/clean-session-bloat.sh`
- **Typical sizes**: healthy <2MB, bloated 5-15MB, extreme >20MB
