#!/usr/bin/env python3
"""Karman build: fetch components from manifest.toml, overlay base/ + lang/,
write dist/karman-<version>.zip. Python 3.11+, stdlib only."""
import argparse
import datetime
import fnmatch
import hashlib
import json
import os
import re
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
# edited by the user, so the on-console update zip must never overwrite them
USER_OWNED = (
    "bootloader/hekate_ipl.ini",
    "config/ultrahand/config.ini",
    "config/sys-ftpd/config.ini",  # port + password
    "config/Fizeau/config.ini",
)


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
        e.close()
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
        strip, root, wrote = c.get("strip", 0), dest.resolve(), 0
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
                wrote += 1
        if not wrote:
            raise BuildError("archive produced no files (wrong strip/exclude?)")
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
        assets = {a["name"]: a for a in rel["assets"]}
        name = pick_asset(list(assets), c["asset"])
        return rel["tag_name"], name, assets[name]["browser_download_url"], assets[name].get("updated_at", "")
    if src == "url":
        return "url", Path(c["url"]).name, c["url"], ""
    if src == "local":
        return "local", Path(c["path"]).name, c["path"], ""

    raise BuildError(f"unknown source {src!r}")


def fetch(c, url, name, cache, stamp=""):
    if c["source"] == "local":
        return Path(url)
    # key includes the asset's updated_at, so a rolling tag (same URL, new bytes) is refetched
    dest = cache / hashlib.sha256((url + stamp).encode()).hexdigest()[:16] / name
    if c["source"] == "github" and dest.exists():
        return dest
    data = http(url)
    if not data:
        raise BuildError(f"empty download from {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    tmp.write_bytes(data)
    tmp.replace(dest)  # atomic: an interrupted download never poisons the cache
    return dest


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fetch_verified(c, cache):
    try:
        tag, name, url, stamp = resolve(c)
        f = fetch(c, url, name, cache, stamp)
        if f.stat().st_size == 0:
            raise BuildError(f"{f.name} is empty")
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
    shutil.copytree(root / "lang/en", stage, dirs_exist_ok=True)  # en is the live default
    if (root / "base").is_dir():  # last, so the user's files win
        shutil.copytree(root / "base", stage, dirs_exist_ok=True)
    for l in LANGS:
        shutil.copytree(root / "lang" / l, stage / "karman/lang" / l, dirs_exist_ok=True)


UPDATE_ASSET = "karman-update.zip"
DL = "/config/ultrahand/downloads"


def update_sections(release):
    out = []
    if repo := release.get("repo"):
        url = f"https://github.com/{repo}/releases/latest/download/{UPDATE_ASSET}"
        out += [
            "[Update Karman (reboot after)]",
            f"delete {DL}/{UPDATE_ASSET}",
            f"delete {DL}/karman-update/",  # leftovers from an interrupted run must not mix in
            f"download {url} {DL}/{UPDATE_ASSET}",
            f"unzip {DL}/{UPDATE_ASSET} {DL}/karman-update/",
            f"move {DL}/karman-update/ /",
            f"delete {DL}/{UPDATE_ASSET}",
            "",
        ]
    if fw := release.get("firmware_url"):
        out += [
            "[Download firmware (then open Daybreak)]",
            f"delete {DL}/firmware.zip",
            f"download {fw} {DL}/firmware.zip",
            f"unzip {DL}/firmware.zip /firmware/",
            f"delete {DL}/firmware.zip",
            "",
        ]
    return out


def write_package(stage, release=None):
    # ponytail: whole-file copy resets other Ultrahand settings (combo, theme);
    # switch to an ini-edit command if Ultrahand exposes one.
    lines = update_sections(release or {})
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


def write_zip(stage, out, skip=()):
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    try:
        with zipfile.ZipFile(tmp, "w") as z:
            for p in sorted(stage.rglob("*")):
                rel = p.relative_to(stage).as_posix()
                if p.is_file() and rel not in skip:
                    zi = zipfile.ZipInfo(rel, (1980, 1, 1, 0, 0, 0))
                    zi.compress_type = zipfile.ZIP_DEFLATED
                    zi.external_attr = 0o644 << 16
                    z.writestr(zi, p.read_bytes())
        tmp.replace(out)
    finally:
        tmp.unlink(missing_ok=True)


RELEASE_KEYS = ("repo", "firmware_url")
REPO_RE = re.compile(r"[\w.-]+/[\w.-]+")
URL_RE = re.compile(r"https://[^\s\[\];]+")  # these values are written into package.ini lines


def release_cfg(data):
    r = data.get("release", {})
    if not isinstance(r, dict):
        raise BuildError("[release] must be a table")
    for k in r:
        if k not in RELEASE_KEYS:
            raise BuildError(f"[release] unknown key {k!r} (allowed: {', '.join(RELEASE_KEYS)})")
    if "repo" in r and not (isinstance(r["repo"], str) and REPO_RE.fullmatch(r["repo"])):
        raise BuildError('[release] repo must look like "owner/name"')
    if "firmware_url" in r and not (isinstance(r["firmware_url"], str) and URL_RE.fullmatch(r["firmware_url"])):
        raise BuildError("[release] firmware_url must be an https:// URL without spaces, [ ] or ;")
    return r


def build(root, manifest, out, cache, version="dev"):
    update = out.with_name("karman-update.zip")
    for z in (out, update):
        z.unlink(missing_ok=True)  # first, so ANY failure below leaves no older zip looking current
    data = tomllib.loads(manifest.read_text())
    comps, release = data["component"], release_cfg(data)
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
        write_package(stage, release)
        text = json.dumps(lock, indent=2, sort_keys=True) + "\n"
        (stage / "karman").mkdir(exist_ok=True)
        (stage / "karman/lock.json").write_text(text)
        (stage / "karman/version.txt").write_text(version + "\n")
        try:
            write_zip(stage, out)
            write_zip(stage, update, skip=USER_OWNED)
        except BaseException:
            for z in (out, update):  # never ship half a release
                z.unlink(missing_ok=True)
            raise
        (root / "lock.json").write_text(text)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the Karman SD-card zip")
    ap.add_argument("--version", default=datetime.date.today().strftime("%Y.%m.%d"))
    ap.add_argument("--manifest", default=ROOT / "manifest.toml", type=Path)
    ap.add_argument("--out", default=ROOT / "dist", type=Path)
    a = ap.parse_args(argv)
    try:
        print(build(ROOT, a.manifest, a.out / f"karman-{a.version}.zip", ROOT / ".cache", a.version))
    except BuildError as e:
        raise SystemExit(f"build failed: {e}")


if __name__ == "__main__":
    main()
