"""Run repository checks without changing tracked files."""
from pathlib import Path
import argparse
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    if args.write_report:
        (ROOT / "validation").mkdir(exist_ok=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
    commands = [
        [sys.executable, "-B", "-X", "utf8", str(ROOT / "tools" / name)]
        for name in (
            "validate.py",
            "check_retrieval.py",
            "check_review_workflow.py",
            "check_game.py",
            "check_v14.py",
            "check_v15.py",
            "check_v16.py",
            "check_v17.py",
            "check_v18.py",
            "check_v19.py",
        )
    ]
    commands.append(["node", str(ROOT / "tools/validate_schema.js")])
    for command in commands:
        print(f"Checking {Path(command[-1]).name}", flush=True)
        if args.write_report:
            command.append("--write-report")
        try:
            result = subprocess.run(command, cwd=ROOT, env=env, check=False)
        except FileNotFoundError:
            print("Schema validation requires Node.js and npm ci.", file=sys.stderr)
            return 1
        if result.returncode:
            return result.returncode
    print("All eleven validation tools passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
