#!/usr/bin/env python3
import hashlib, json, argparse
from pathlib import Path

def sha256sum(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def scan_directory(directory):
    result = {}
    for file in Path(directory).rglob("*"):
        if file.is_file():
            result[str(file)] = sha256sum(file)
    return result

def save_snapshot(snapshot, output):
    with open(output, "w") as f:
        json.dump(snapshot, f, indent=4)

def verify_snapshot(snapshot_file):
    with open(snapshot_file) as f:
        old = json.load(f)

    for path, old_hash in old.items():
        p = Path(path)
        if not p.exists():
            print(f"[MISSING] {path}")
            continue

        new_hash = sha256sum(p)
        if new_hash != old_hash:
            print(f"[MODIFIED] {path}")
        else:
            print(f"[OK]       {path}")

def main():
    parser = argparse.ArgumentParser(
        description="File Integrity Checker"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    scan_cmd = sub.add_parser("scan")
    scan_cmd.add_argument("directory")

    save_cmd = sub.add_parser("save")
    save_cmd.add_argument("directory")
    save_cmd.add_argument("output")

    verify_cmd = sub.add_parser("verify")
    verify_cmd.add_argument("snapshot")

    args = parser.parse_args()

    if args.command == "scan":
        snap = scan_directory(args.directory)
        print(json.dumps(snap, indent=4))

    elif args.command == "save":
        snap = scan_directory(args.directory)
        save_snapshot(snap, args.output)

    elif args.command == "verify":
        verify_snapshot(args.snapshot)

if __name__ == "__main__":
    main()