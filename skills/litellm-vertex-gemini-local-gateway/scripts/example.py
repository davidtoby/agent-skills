#!/usr/bin/env python3
"""Quick verifier for a local LiteLLM Vertex Gemini gateway.

Usage:
  python3 example.py --base-url http://127.0.0.1:4000 --api-key "$LITELLM_MASTER_KEY" --model gemini-3.1-pro-preview
"""

import argparse
import json
import urllib.request


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--base-url', required=True)
    p.add_argument('--api-key', required=True)
    p.add_argument('--model', default='gemini-3.1-pro-preview')
    args = p.parse_args()

    payload = json.dumps({
        'model': args.model,
        'max_tokens': 32,
        'messages': [{'role': 'user', 'content': 'Reply with exactly: gateway-ok'}],
    }).encode()

    req = urllib.request.Request(
        args.base_url.rstrip('/') + '/v1/messages',
        data=payload,
        headers={
            'Authorization': f'Bearer {args.api_key}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        print(r.read().decode())


if __name__ == '__main__':
    main()
