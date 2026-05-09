#!/usr/bin/env python3
import argparse
from pathlib import Path


def write(path: Path, content: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    if executable:
        path.chmod(0o755)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--output-dir', required=True)
    p.add_argument('--label', required=True)
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', default='4000')
    p.add_argument('--model-alias', default='gemini-3.1-pro-preview')
    p.add_argument('--vertex-model', default='vertex_ai/gemini-3.1-pro-preview')
    args = p.parse_args()

    out = Path(args.output_dir).expanduser().resolve()
    start_path = out / 'scripts' / 'start.sh'
    logs_dir = out / 'logs'

    env_example = f'''VERTEXAI_PROJECT=your-gcp-project-id
VERTEXAI_LOCATION=global
LITELLM_MASTER_KEY=replace-with-a-random-secret
LITELLM_HOST={args.host}
LITELLM_PORT={args.port}
'''

    litellm_yaml = f'''model_list:
  - model_name: {args.model_alias}
    litellm_params:
      model: {args.vertex_model}
      vertex_project: os.environ/VERTEXAI_PROJECT
      vertex_location: os.environ/VERTEXAI_LOCATION

litellm_settings:
  master_key: os.environ/LITELLM_MASTER_KEY

general_settings:
  ui: false
  telemetry: false
'''

    env_sh = '''#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$BASE_DIR/.env"
CONFIG_FILE="$BASE_DIR/config/litellm.yaml"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

export NO_PROXY="127.0.0.1,localhost,::1"
export no_proxy="$NO_PROXY"
export PYTHONNOUSERSITE=1
export LITELLM_CONFIG="$CONFIG_FILE"
export LITELLM_HOST="${LITELLM_HOST:-127.0.0.1}"
export LITELLM_PORT="${LITELLM_PORT:-4000}"
'''

    start_sh = '''#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$BASE_DIR/scripts/env.sh"
exec "$HOME/.local/bin/litellm" --config "$LITELLM_CONFIG" --host "$LITELLM_HOST" --port "$LITELLM_PORT"
'''

    health_sh = '''#!/usr/bin/env bash
set -euo pipefail
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
source "$BASE_DIR/scripts/env.sh"

printf 'GET /health\\n'
curl -sS --fail "http://${LITELLM_HOST}:${LITELLM_PORT}/health" || true
printf '\\n\\nGET /v1/models\\n'
curl -sS --fail \\
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \\
  "http://${LITELLM_HOST}:${LITELLM_PORT}/v1/models"
printf '\\n'
'''

    plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "https://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>{args.label}</string>
    <key>ProgramArguments</key>
    <array>
      <string>/bin/bash</string>
      <string>{start_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>{out}</string>
    <key>StandardOutPath</key>
    <string>{logs_dir / 'stdout.log'}</string>
    <key>StandardErrorPath</key>
    <string>{logs_dir / 'stderr.log'}</string>
  </dict>
</plist>
'''

    write(out / '.env.example', env_example)
    write(out / 'config' / 'litellm.yaml', litellm_yaml)
    write(out / 'scripts' / 'env.sh', env_sh, executable=True)
    write(start_path, start_sh, executable=True)
    write(out / 'scripts' / 'health.sh', health_sh, executable=True)
    write(out / 'launchd' / f'{args.label}.plist', plist)
    logs_dir.mkdir(parents=True, exist_ok=True)

    print(out)
    print(out / '.env.example')
    print(out / 'config' / 'litellm.yaml')
    print(out / 'scripts' / 'env.sh')
    print(start_path)
    print(out / 'scripts' / 'health.sh')
    print(out / 'launchd' / f'{args.label}.plist')


if __name__ == '__main__':
    main()
