#!/usr/bin/env python3
"""Karman build: fetch components from manifest.toml, overlay base/ + lang/,
write dist/karman-<version>.zip. Python 3.11+, stdlib only."""
import argparse
import datetime
import fnmatch
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import tomllib
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LANGS = {"en": "English", "ptbr": "Português (BR)", "es": "Español"}


class BuildError(Exception):
    pass


def http(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": "karman-build", **(headers or {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def api(path):
    h = {"Accept": "application/vnd.github+json"}
    if tok := os.environ.get("GITHUB_TOKEN"):  # only ever sent to api.github.com
        h["Authorization"] = f"Bearer {tok}"
    return json.loads(http(f"https://api.github.com/{path}", h))


def pick_asset(names, pattern):
    hits = [n for n in names if fnmatch.fnmatch(n, pattern)]
    if len(hits) != 1:
        raise BuildError(f"asset glob {pattern!r} matched {len(hits)} of {names}")
    return hits[0]


def install(c, f, stage):
    dest = stage / c.get("dest", "").strip("/")
    dest.mkdir(parents=True, exist_ok=True)
    kind = c.get("kind", "zip" if f.suffix == ".zip" else "file")
    if kind == "zip":
        with zipfile.ZipFile(f) as z:
            z.extractall(dest)  # zipfile strips absolute paths and '..'
    elif kind == "7z":  # ponytail: needs bsdtar (macOS/most Linux); py7zr if it ever fails
        subprocess.run(["tar", "-xf", str(f), "-C", str(dest)], check=True)
    else:
        shutil.copy2(f, dest / c.get("rename", f.name))
