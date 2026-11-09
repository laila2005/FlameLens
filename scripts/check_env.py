#!/usr/bin/env python3
"""Check that this computer has the tools the team needs.

Run:  python scripts/check_env.py

REQUIRED items must be OK for everyone. ROLE items matter for the roles listed.
Nothing here installs anything or touches the network.
"""
import shutil
import subprocess
import sys


def run(cmd):
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return (out.stdout or out.stderr).strip().splitlines()[0] if (out.stdout or out.stderr) else ""
    except Exception:
        return ""


def version_tuple(text):
    digits = "".join(c if (c.isdigit() or c == ".") else " " for c in text).split()
    for chunk in digits:
        parts = chunk.split(".")
        if parts and parts[0].isdigit():
            return tuple(int(p) for p in parts if p.isdigit())
    return ()


CHECKS = [
    # (name, kind, command, minimum, roles, hint)
    ("Python", "REQUIRED", None, (3, 11), "everyone", "Install Python 3.11 or newer from python.org"),
    ("git", "REQUIRED", ["git", "--version"], (2, 30), "everyone", "Install git from git-scm.com"),
    ("Node.js", "ROLE", ["node", "--version"], (20, 0), "A, B, C", "Install Node 20 or newer from nodejs.org"),
    ("npm", "ROLE", ["npm", "--version"], (9, 0), "A, B, C", "Comes with Node.js"),
    ("GitHub CLI (gh)", "OPTIONAL", ["gh", "--version"], (2, 0), "A", "Optional, makes labels and PRs faster: cli.github.com"),
    ("Docker", "OPTIONAL", ["docker", "--version"], (20, 0), "A", "Optional, only for deployment tests"),
    ("Ollama", "ROLE", ["ollama", "--version"], (0, 1), "E", "Install from ollama.com, then pull a small model"),
]


def main():
    print("FlameLens environment check\n")
    failures = 0
    for name, kind, cmd, minimum, roles, hint in CHECKS:
        if cmd is None:
            ver = sys.version_info[:3]
            found = ".".join(map(str, ver))
            ok = ver >= minimum
        else:
            exe = shutil.which(cmd[0])  # full path, so Windows .cmd files (npm) also work
            if exe is None:
                found, ok = "", False
            else:
                found = run([exe] + cmd[1:])
                v = version_tuple(found)
                ok = bool(v) and v >= minimum
        if ok:
            status = "OK"
        elif kind == "REQUIRED":
            status = "MISSING"
            failures += 1
        else:
            status = "MISSING" if kind == "ROLE" else "skip"
        shown = found if found else "not found"
        print(f"[{status:7}] {name:16} {kind:8} roles: {roles:9} {shown}")
        if status == "MISSING":
            print(f"          -> {hint}")
    print()
    if failures:
        print("Some REQUIRED tools are missing. Fix them and run again.")
        sys.exit(1)
    print("All REQUIRED tools are OK. Fix any MISSING item that is marked for your role.")


if __name__ == "__main__":
    main()
