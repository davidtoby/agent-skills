#!/usr/bin/env python3
import sys
import os
import json
import argparse
import subprocess
import shutil

def parse_args():
    parser = argparse.ArgumentParser(description="Validate, package, preview, and send Feishu Interactive Cards via lark-cli")
    parser.add_argument("--card", required=True, help="Path to .card file or card JSON file")
    parser.add_argument("--user-id", required=True, help="Recipient user open_id (ou_xxx)")
    parser.add_argument("--name", help="Card name (default derived from filename)")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print payload without sending")
    return parser.parse_args()

def main():
    args = parse_args()
    card_path = os.path.abspath(args.card)
    
    if not os.path.exists(card_path):
        print(f"Error: File not found: {card_path}", file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(card_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except Exception as e:
        print(f"Error parsing JSON from {card_path}: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Check if raw_data is already CardKit wrapped or plain DSL
    if "dsl" in raw_data and isinstance(raw_data["dsl"], dict):
        card_name = raw_data.get("name") or args.name or os.path.splitext(os.path.basename(card_path))[0]
        dsl = raw_data["dsl"]
    else:
        card_name = args.name or os.path.splitext(os.path.basename(card_path))[0]
        dsl = raw_data

    card_kit_data = {
        "name": card_name,
        "dsl": dsl,
        "variables": []
    }
    
    # Overwrite .card file with proper CardKit format if needed
    card_filename = f"{card_name}.card" if not card_name.endswith(".card") else card_name
    cwd_card_path = os.path.join(os.getcwd(), card_filename)
    with open(cwd_card_path, "w", encoding="utf-8") as f:
        json.dump(card_kit_data, f, ensure_ascii=False, indent=2)
        
    print(f"✅ CardKit envelope prepared at: {cwd_card_path}")

    # Build Interactive Card preview payload
    card_payload = {
        "receive_id": args.user_id,
        "msg_type": "interactive",
        "content": json.dumps(dsl, ensure_ascii=False)
    }
    
    payload_file = os.path.join(os.getcwd(), "_send_card_payload.json")
    with open(payload_file, "w", encoding="utf-8") as f:
        json.dump(card_payload, f, ensure_ascii=False)
        
    if args.dry_run:
        print("🔍 [Dry Run] Interactive Card payload preview:")
        print(json.dumps(card_payload, indent=2, ensure_ascii=False))
        return

    # Step 1: Send Interactive Card Preview
    print("🚀 Sending Interactive Card preview to user...")
    cmd1 = [
        "lark-cli", "api", "POST", "/open-apis/im/v1/messages",
        "--params", '{"receive_id_type":"open_id"}',
        "--data", f"@{os.path.basename(payload_file)}",
        "--as", "bot"
    ]
    res1 = subprocess.run(cmd1, capture_output=True, text=True)
    if res1.returncode != 0 or '"ok":true' not in res1.stdout.replace(" ", ""):
        print(f"❌ Failed to send card preview: {res1.stderr or res1.stdout}", file=sys.stderr)
        sys.exit(1)
    print("✅ Interactive Card preview sent successfully!")

    # Step 2: Upload .card file
    print("📦 Uploading .card file to Feishu...")
    rel_card_file = os.path.basename(cwd_card_path)
    cmd2 = [
        "lark-cli", "api", "POST", "/open-apis/im/v1/files",
        "--file", f"file={rel_card_file}",
        "--data", json.dumps({"file_type": "stream", "file_name": rel_card_file}),
        "--as", "bot"
    ]
    res2 = subprocess.run(cmd2, capture_output=True, text=True)
    try:
        data2 = json.loads(res2.stdout)
        file_key = data2.get("data", {}).get("file_key")
    except Exception:
        file_key = None

    if not file_key:
        print(f"⚠️ Warning: Could not retrieve file_key from response: {res2.stdout}", file=sys.stderr)
        file_key_msg = None
    else:
        # Step 3: Send file message
        print("📄 Sending .card file attachment...")
        file_payload = {
            "receive_id": args.user_id,
            "msg_type": "file",
            "content": json.dumps({"file_key": file_key}, ensure_ascii=False)
        }
        file_payload_file = os.path.join(os.getcwd(), "_send_file_payload.json")
        with open(file_payload_file, "w", encoding="utf-8") as f:
            json.dump(file_payload, f, ensure_ascii=False)
            
        cmd3 = [
            "lark-cli", "api", "POST", "/open-apis/im/v1/messages",
            "--params", '{"receive_id_type":"open_id"}',
            "--data", f"@{os.path.basename(file_payload_file)}",
            "--as", "bot"
        ]
        res3 = subprocess.run(cmd3, capture_output=True, text=True)
        if res3.returncode == 0:
            print("✅ .card file attachment sent successfully!")

    # Cleanup temp payload files
    for p in [payload_file, os.path.join(os.getcwd(), "_send_file_payload.json")]:
        if os.path.exists(p):
            os.remove(p)

if __name__ == "__main__":
    main()
