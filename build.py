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
import urllib.error
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
    try:
        return json.loads(http(f"https://api.github.com/{path}", h))
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            raise BuildError("GitHub API rate limit hit; set GITHUB_TOKEN (e.g. GITHUB_TOKEN=$(gh auth token)) and retry") from e
        raise


def pick_asset(names, pattern):
    hits = [n for n in names if fnmatch.fnmatch(n, pattern)]
    if len(hits) != 1:
        raise BuildError(f"asset glob {pattern!r} matched {len(hits)} of {names}")
    return hits[0]


def install(c, f, stage):
    dest = stage / c.get("dest", "").strip("/")
    dest.mkdir(parents=True, exist_ok=True)
    kind = c.get("kind", "zip" if f.suffix == ".zip" else "file")
    exclude = c.get("exclude", [])
    if kind == "zip":
        strip, root = c.get("strip", 0), dest.resolve()
        with zipfile.ZipFile(f) as z:
            for info in z.infolist():
                rel = "/".join(info.filename.split("/")[strip:])
                if info.is_dir() or not rel or any(fnmatch.fnmatch(rel, p) for p in exclude):
                    continue
                target = (root / rel).resolve()
                if not target.is_relative_to(root):
                    raise BuildError(f"unsafe path in archive: {info.filename}")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(z.read(info))
    elif kind == "7z":  # ponytail: needs bsdtar (macOS/most Linux); py7zr if it ever fails
        ex = [f"--exclude={p}" for p in exclude]
        subprocess.run(["tar", "-xf", str(f), "-C", str(dest), *ex], check=True)
    else:
        shutil.copy2(f, dest / c.get("rename", f.name))


def resolve(c):
    src = c["source"]
    if src == "github":
        ref = f"tags/{c['pin']}" if "pin" in c else "latest"
        rel = api(f"repos/{c['repo']}/releases/{ref}")
        assets = {a["name"]: a["browser_download_url"] for a in rel["assets"]}
        name = pick_asset(list(assets), c["asset"])
        return rel["tag_name"], name, assets[name]
    if src == "url":
        return "url", Path(c["url"]).name, c["url"]
    if src == "local":
        return "local", Path(c["path"]).name, c["path"]
    raise BuildError(f"unknown source {src!r}")


def fetch(c, url, name, cache):
    if c["source"] == "local":
        return Path(url)
    dest = cache / hashlib.sha256(url.encode()).hexdigest()[:16] / name
    if c["source"] == "github" and dest.exists():  # asset URLs embed the tag: never stale
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(http(url))
    return dest


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fetch_verified(c, cache):
    try:
        tag, name, url = resolve(c)
        f = fetch(c, url, name, cache)
        digest = sha256(f)
        if c.get("sha256", digest) != digest:
            raise BuildError(f"sha256 mismatch: expected {c['sha256']}, got {digest}")
        return tag, name, f, digest
    except Exception as e:
        raise BuildError(f"{c['name']}: {e}") from e


def apply_overlays(root, stage):
    for l in LANGS:
        if not (root / "lang" / l).is_dir():
            raise BuildError(f"missing lang/{l}")
    if (root / "base").is_dir():
        shutil.copytree(root / "base", stage, dirs_exist_ok=True)
    shutil.copytree(root / "lang/en", stage, dirs_exist_ok=True)  # en is the live default
    for l in LANGS:
        shutil.copytree(root / "lang" / l, stage / "karman/lang" / l, dirs_exist_ok=True)


def write_lang_package(stage):
    # ponytail: whole-file copy resets other Ultrahand settings (combo, theme);
    # switch to an ini-edit command if Ultrahand exposes one.
    lines = []
    for l, title in LANGS.items():
        base = stage / "karman/lang" / l
        lines.append(f"[{title}]")
        for f in sorted(p for p in base.rglob("*") if p.is_file()):
            rel = f.relative_to(base)
            lines.append(f"copy /karman/lang/{l}/{rel.as_posix()} /{rel.parent.as_posix()}/")
        lines.append("")
    pkg = stage / "switch/.packages/Karman"
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "package.ini").write_text("\n".join(lines), encoding="utf-8")


def write_zip(stage, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w") as z:
        for p in sorted(stage.rglob("*")):
            if p.is_file():
                zi = zipfile.ZipInfo(p.relative_to(stage).as_posix(), (1980, 1, 1, 0, 0, 0))
                zi.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(zi, p.read_bytes())
    tmp.replace(out)


def build(root, manifest, out, cache):
    comps = tomllib.loads(manifest.read_text())["component"]
    lock = {}
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp) / "sd"
        stage.mkdir()
        for c in comps:
            tag, name, f, digest = fetch_verified(c, cache)
            try:
                install(c, f, stage)
            except Exception as e:
                raise BuildError(f"{c['name']}: {e}") from e
            lock[c["name"]] = {"tag": tag, "asset": name, "sha256": digest}
        apply_overlays(root, stage)
        write_lang_package(stage)
        text = json.dumps(lock, indent=2, sort_keys=True) + "\n"
        (root / "lock.json").write_text(text)
        (stage / "karman").mkdir(exist_ok=True)
        (stage / "karman/lock.json").write_text(text)
        write_zip(stage, out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the Karman SD-card zip")
    ap.add_argument("--version", default=datetime.date.today().strftime("%Y.%m.%d"))
    ap.add_argument("--manifest", default=ROOT / "manifest.toml", type=Path)
    ap.add_argument("--out", default=ROOT / "dist", type=Path)
    a = ap.parse_args(argv)
    try:
        print(build(ROOT, a.manifest, a.out / f"karman-{a.version}.zip", ROOT / ".cache"))
    except BuildError as e:
        raise SystemExit(f"build failed: {e}")


if __name__ == "__main__":
    main()
