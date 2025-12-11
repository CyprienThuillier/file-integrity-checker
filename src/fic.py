#!/usr/bin/env python3
import hashlib, json, argparse
from pathlib import Path

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

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
      print(f"{YELLOW}[MISSING]{RESET} {path}")
      continue

    new_hash = sha256sum(p)

    if new_hash != old_hash:
      print(f"{RED}[MODIFIED]{RESET} {path}")
    else:
      print(f"{GREEN}[OK]{RESET} {path}")


def main():
  parser = argparse.ArgumentParser(
    description="File Integrity Checker"
  )

  sub = parser.add_subparsers(dest="command", required=True)

  scan_cmd = sub.add_parser("scan")
  scan_cmd.add_argument("directory")

  save_cmd = sub.add_parser("save")
  save_cmd.add_argument("directory")
  save_cmd.add_argument("-o", "--output", default=None)

  check_cmd = sub.add_parser("check")
  check_cmd.add_argument("snapshot")

  args = parser.parse_args()

  if args.command == "scan":
    snap = scan_directory(args.directory)
    print(json.dumps(snap, indent=4))

  elif args.command == "save":
    snap = scan_directory(args.directory)

    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"
    DATA_DIR.mkdir(exist_ok=True)

    if args.output is None:
      dir_name = Path(args.directory).name
      snap_name = DATA_DIR / f"snapshot_{dir_name}.json"
    else:
      snap_name = args.output

    save_snapshot(snap, snap_name)
    print(f"{GREEN}[+]{RESET} Snapshot saved to {snap_name}")

  elif args.command == "check":
    pass
    verify_snapshot(args.snapshot)

if __name__ == "__main__":
    main()
