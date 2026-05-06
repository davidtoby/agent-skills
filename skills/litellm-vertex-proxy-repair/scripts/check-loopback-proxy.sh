#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
import os
import urllib.request

print('python_proxies=', urllib.request.getproxies())
print('NO_PROXY=', os.environ.get('NO_PROXY', ''))
print('no_proxy=', os.environ.get('no_proxy', ''))
PY
