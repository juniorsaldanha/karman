# Karman On-Console Updater Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `build.py` also emits `karman-update.zip` (the pack minus user-owned config), stamps `karman/version.txt`, and generates "Update Karman" (and optional "Download firmware") entries in the Karman Ultrahand package; docs explain updating and publishing releases.

**Architecture:** Extend the existing single-file build. A `[release]` table in `manifest.toml` supplies the GitHub repo (and optional firmware URL). The stage dir is zipped twice (full, and update with `USER_OWNED` skipped). `write_lang_package` becomes `write_package` and appends the updater sections to the same `package.ini`. No new dependencies, no compiled code.

**Tech Stack:** Python 3.11+ stdlib only; `unittest`. Run Python as `/opt/homebrew/bin/python3.14` on this machine.

**Spec:** `docs/superpowers/specs/2026-10-14-karman-updater-design.md` (extends `2026-10-14-karman-design.md`)

## Global Constraints

- Stdlib only; Python 3.11+.
- GitHub repo: `juniorsaldanha/karman`. Update URL: `https://github.com/juniorsaldanha/karman/releases/latest/download/karman-update.zip` (asset name is constant: `karman-update.zip`).
- `USER_OWNED = ("bootloader/hekate_ipl.ini", "config/ultrahand/config.ini")`. These are never in `karman-update.zip`.
- Karman ships no firmware and no firmware source; the firmware entry exists only if `release.firmware_url` is set.
- No creating the GitHub repo, no `git push`, no `gh release create` by the agent.
- A failed build leaves no `karman-<ver>.zip` and no `karman-update.zip`; builds stay byte-reproducible.
- Nothing here has run on a console; docs must say so.

## Spec deviation (ruled in advance)

The spec says the update entry should "show a reboot message". Ultrahand's `notify`-style command is not verified, so the reboot instruction is carried in the section title: `[Update Karman (reboot after)]`. Task 1 edits the spec line to match.

## Review Focus

- The update zip contains every file of the full zip except exactly `USER_OWNED` (an update must never overwrite the user's boot menu or Ultrahand settings). Task 1.
- `release.repo` unset → no update URL and no half-broken entry in `package.ini`. Task 2.
- `[release]` values of the wrong type → the build fails naming the key, not a traceback. Task 1.
- A failed build must not leave a stale `karman-update.zip` that a later `gh release create` could publish as current. Task 1.
- `karman/version.txt` is in both zips and equals the build version, so an on-console update bumps the displayed version. Task 1.

---

## File Structure

```
build.py                         modified: release_cfg, USER_OWNED, write_zip(skip), write_package, build(version)
test_build.py                    modified: new Update/Package test classes
manifest.toml                    modified: [release] table
docs/{en,ptbr,es}/updating.md    new
docs/{en,ptbr,es}/how-to.md      modified: "Updating Karman" points to updating.md
README.md                        modified: docs table row, publish note
```

---

### Task 1: Update zip, version stamp, release config

**Files:** Modify `build.py`, `test_build.py`, `docs/superpowers/specs/2026-10-14-karman-updater-design.md`

**Interfaces:**
- Consumes (existing): `write_zip(stage, out)`, `build(root, manifest, out, cache)`, `BuildError`
- Produces: `USER_OWNED: tuple[str,...]`, `release_cfg(data: dict) -> dict`, `write_zip(stage: Path, out: Path, skip=()) -> None`, `build(root, manifest, out, cache, version="dev") -> Path`, update zip at `out.with_name("karman-update.zip")`, stage file `karman/version.txt` (`<version>\n`)

- [ ] **Step 1: Edit the spec line** in "Build changes" item 4: replace "then show a "reboot to apply" message" with "the section title carries the reboot instruction (`[Update Karman (reboot after)]`), because a notify command is unverified". Commit with the code later.

- [ ] **Step 2: Write failing tests** — add to `test_build.py` (reuse `make_root`; add the helper and a class):

```python
def add_base(root):
    (root / "base/bootloader").mkdir(parents=True)
    (root / "base/bootloader/hekate_ipl.ini").write_text("[config]\n")


def with_release(root, text):
    m = root / "manifest.toml"
    m.write_text(text + "\n" + m.read_text())


class Update(unittest.TestCase):
    def run_build(self, root, version="9.9", name="out.zip"):
        return build.build(root, root / "manifest.toml", root / "dist" / name, root / ".cache", version)

    def test_update_zip_is_full_minus_user_owned(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            add_base(root)
            full = set(zipfile.ZipFile(self.run_build(root)).namelist())
            upd = set(zipfile.ZipFile(root / "dist/karman-update.zip").namelist())
            self.assertEqual(full - upd, set(build.USER_OWNED))
            self.assertEqual(upd - full, set())

    def test_update_zip_deterministic(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            self.run_build(root, name="1.zip")
            a = (root / "dist/karman-update.zip").read_bytes()
            self.run_build(root, name="2.zip")
            self.assertEqual(a, (root / "dist/karman-update.zip").read_bytes())

    def test_version_txt_in_both_zips(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            full = zipfile.ZipFile(self.run_build(root, version="1.2.3"))
            upd = zipfile.ZipFile(root / "dist/karman-update.zip")
            self.assertEqual(full.read("karman/version.txt"), b"1.2.3\n")
            self.assertEqual(upd.read("karman/version.txt"), b"1.2.3\n")

    def test_bad_release_type_names_key(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            with_release(root, "[release]\nrepo = 5")
            with self.assertRaisesRegex(build.BuildError, "repo"):
                self.run_build(root)

    def test_failed_build_removes_stale_update_zip(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            self.run_build(root)
            (root / "fix/a.zip").write_bytes(b"not a zip")
            with self.assertRaises(build.BuildError):
                self.run_build(root)
            self.assertFalse((root / "dist/karman-update.zip").exists())
```

- [ ] **Step 3: Run, verify FAIL** — `/opt/homebrew/bin/python3.14 -m unittest test_build.Update -v` → errors: `build()` takes no `version`, no `USER_OWNED`.

- [ ] **Step 4: Implement** in `build.py`:

```python
USER_OWNED = ("bootloader/hekate_ipl.ini", "config/ultrahand/config.ini")


def release_cfg(data):
    r = data.get("release", {})
    for k in ("repo", "firmware_url"):
        if k in r and not isinstance(r[k], str):
            raise BuildError(f"[release] {k} must be a string")
    return r
```

Change `write_zip` signature to `write_zip(stage, out, skip=())` and its loop condition to:

```python
            for p in sorted(stage.rglob("*")):
                rel = p.relative_to(stage).as_posix()
                if p.is_file() and rel not in skip:
                    zi = zipfile.ZipInfo(rel, (1980, 1, 1, 0, 0, 0))
```

Change `build` to:

```python
def build(root, manifest, out, cache, version="dev"):
    data = tomllib.loads(manifest.read_text())
    comps, release = data["component"], release_cfg(data)
    update = out.with_name("karman-update.zip")
    for z in (out, update):
        z.unlink(missing_ok=True)  # a failed build must not leave an older zip looking current
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
        (stage / "karman").mkdir(exist_ok=True)
        (stage / "karman/lock.json").write_text(text)
        (stage / "karman/version.txt").write_text(version + "\n")
        write_zip(stage, out)
        write_zip(stage, update, skip=USER_OWNED)
        (root / "lock.json").write_text(text)
    return out
```

(`release` is validated here and consumed in Task 2.) In `main`, pass the version: `build(ROOT, a.manifest, a.out / f"karman-{a.version}.zip", ROOT / ".cache", a.version)`.

- [ ] **Step 5: Run the whole suite, verify PASS** — `/opt/homebrew/bin/python3.14 -m unittest` → all pass (21 existing + 5 new = 26).
- [ ] **Step 6: Commit** — `git add -A && git commit -m "Emit karman-update.zip and version.txt; validate [release]"` (end with the Co-Authored-By trailer).

---

### Task 2: Generated updater entries in the Karman package

**Files:** Modify `build.py`, `test_build.py`

**Interfaces:**
- Consumes: `release_cfg` result (`dict` with optional `repo`, `firmware_url`), `LANGS`
- Produces: `write_package(stage: Path, release: dict | None = None) -> None` (replaces `write_lang_package`), `UPDATE_ASSET = "karman-update.zip"`

- [ ] **Step 1: Write failing tests** — add to `test_build.py`:

```python
class Package(unittest.TestCase):
    def pkg(self, release_toml=""):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            if release_toml:
                with_release(root, release_toml)
            z = zipfile.ZipFile(build.build(root, root / "manifest.toml", root / "dist/o.zip", root / ".cache"))
            return z.read("switch/.packages/Karman/package.ini").decode()

    def test_update_section_when_repo_set(self):
        p = self.pkg('[release]\nrepo = "o/r"')
        self.assertIn("[Update Karman (reboot after)]", p)
        want = [
            "download https://github.com/o/r/releases/latest/download/karman-update.zip /config/ultrahand/downloads/karman-update.zip",
            "unzip /config/ultrahand/downloads/karman-update.zip /config/ultrahand/downloads/karman-update/",
            "move /config/ultrahand/downloads/karman-update/ /",
            "delete /config/ultrahand/downloads/karman-update.zip",
        ]
        idx = [p.index(w) for w in want]
        self.assertEqual(idx, sorted(idx))

    def test_no_update_section_without_repo(self):
        p = self.pkg()
        self.assertNotIn("Update Karman", p)
        self.assertNotIn("github.com", p)
        self.assertIn("[English]", p)  # language entries unaffected

    def test_firmware_section_only_with_url(self):
        self.assertNotIn("firmware", self.pkg('[release]\nrepo = "o/r"').lower())
        p = self.pkg('[release]\nrepo = "o/r"\nfirmware_url = "https://example.com/fw.zip"')
        self.assertIn("[Download firmware (then open Daybreak)]", p)
        self.assertIn("download https://example.com/fw.zip /config/ultrahand/downloads/firmware.zip", p)
        self.assertIn("unzip /config/ultrahand/downloads/firmware.zip /firmware/", p)

    def test_firmware_url_alone_does_not_need_repo(self):
        p = self.pkg('[release]\nfirmware_url = "https://example.com/fw.zip"')
        self.assertIn("Download firmware", p)
        self.assertNotIn("Update Karman", p)
```

- [ ] **Step 2: Run, verify FAIL** — `python3.14 -m unittest test_build.Package -v` → assertions fail (no sections generated).

- [ ] **Step 3: Implement** — replace `write_lang_package` with:

```python
UPDATE_ASSET = "karman-update.zip"
DL = "/config/ultrahand/downloads"


def update_sections(release):
    out = []
    if repo := release.get("repo"):
        url = f"https://github.com/{repo}/releases/latest/download/{UPDATE_ASSET}"
        out += [
            "[Update Karman (reboot after)]",
            f"delete {DL}/{UPDATE_ASSET}",
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
```

and in `build()` replace `write_lang_package(stage)` with `write_package(stage, release)`.

- [ ] **Step 4: Run the whole suite, verify PASS** — `python3.14 -m unittest` → 30 tests OK (existing `test_zip_contents` still passes: the language lines are unchanged).
- [ ] **Step 5: Commit** — `git commit -am "Generate Update Karman and optional firmware entries"`.

---

### Task 3: Real manifest config and real build check

**Files:** Modify `manifest.toml`

- [ ] **Step 1: Add the release table** at the top of `manifest.toml` (above the first `[[component]]`):

```toml
# On-console updater. repo: GitHub "owner/name" whose latest release carries karman-update.zip.
# firmware_url (optional): a firmware zip URL YOU supply; Karman ships none. Leave unset to omit the entry.
[release]
repo = "juniorsaldanha/karman"
```

- [ ] **Step 2: Real build** — `GITHUB_TOKEN=$(gh auth token) /opt/homebrew/bin/python3.14 build.py --version dev` (expected: prints the zip path, no error).
- [ ] **Step 3: Inspect** —
  - `ls -lh dist/` → both `karman-dev.zip` and `karman-update.zip`; the update zip is slightly smaller.
  - `unzip -p dist/karman-dev.zip karman/version.txt` → `dev`.
  - `unzip -p dist/karman-dev.zip switch/.packages/Karman/package.ini | head -8` → the Update section with the `juniorsaldanha/karman` URL.
  - `diff <(unzip -Z1 dist/karman-dev.zip | sort) <(unzip -Z1 dist/karman-update.zip | sort)` → exactly `bootloader/hekate_ipl.ini` and `config/ultrahand/config.ini`.
- [ ] **Step 4: Reproducibility** — build a second time with `--version dev`, `shasum -a 256` both update zips → identical.
- [ ] **Step 5: Run tests + commit** — `python3.14 -m unittest` then `git commit -am "Configure release repo"`.

---

### Task 4: Docs (en, ptbr, es) and README

**Files:** Create `docs/{en,ptbr,es}/updating.md`; modify `docs/{en,ptbr,es}/how-to.md`, `README.md`

- [ ] **Step 1: Write `docs/en/updating.md`** with this content:

````markdown
# Updating Karman

## On the console (no computer)
1. Connect the Switch to Wi-Fi.
2. Open **Ultrahand** (ZL + ZR + D-Pad Down) → the **Karman** package → **Update Karman (reboot after)**.
3. Wait for the download and extraction to finish.
4. **Reboot** the console (through Hekate) so the new Atmosphere and Hekate files apply.

The update downloads `karman-update.zip` from the latest release of `juniorsaldanha/karman` and extracts it over the SD card. It does **not** touch your boot menu (`bootloader/hekate_ipl.ini`) or Ultrahand settings (`config/ultrahand/config.ini`), so your customizations and chosen language stay. To see what you have installed, open `karman/version.txt` on the SD card.

> **Not tested on a console yet.** Unverified: whether the ~120 MB archive extracts reliably through Ultrahand, how long it takes, and whether overwriting Ultrahand's own files while its overlay runs is safe. Keep your last good full `karman-<version>.zip` on your PC as a fallback. There is no rollback.

If anything fails, update from a computer: extract the full `karman-<version>.zip` over the card ([how-to](how-to.md)).

## Firmware
Karman ships no firmware and has no firmware source. If you set `firmware_url` (below), the package gets a **Download firmware (then open Daybreak)** entry: it downloads your zip to `/firmware/`, then you open **Daybreak** (`switch/daybreak.nro`) and install it. Otherwise copy the firmware files to `/firmware/` yourself. Only use files you trust: Karman does not vouch for the URL.

## Publishing a release (for the maintainer)
1. Build: `GITHUB_TOKEN=$(gh auth token) python3 build.py --version 1.2.0` → `dist/karman-1.2.0.zip` and `dist/karman-update.zip`.
2. Publish both files (the update asset **must** be named `karman-update.zip`):
   ```sh
   gh release create v1.2.0 dist/karman-1.2.0.zip dist/karman-update.zip --title "Karman 1.2.0" --notes "What changed"
   ```
3. Consoles that run **Update Karman** now get this release.

Settings live in the `[release]` table of `manifest.toml`: `repo` (GitHub `owner/name`) and optional `firmware_url`. With no `repo`, the build omits the update entry.
````

- [ ] **Step 2: Translate** to `docs/ptbr/updating.md` and `docs/es/updating.md` (natural wording; commands, paths and entry names unchanged; keep the same number of code blocks).
- [ ] **Step 3: Update `how-to.md` (all three)** — in "Updating Karman", replace the first sentence with a pointer: "On the console: see [updating](updating.md). From a computer: …" (translated; keep the rest).
- [ ] **Step 4: Update `README.md`** — add a docs-table row `Updating | [updating](docs/en/updating.md) | [atualizando](docs/ptbr/updating.md) | [actualizando](docs/es/updating.md)`, and under "Build" add: "Releases: see the *Publishing a release* section of `docs/en/updating.md`."
- [ ] **Step 5: Parity check** —
  ```sh
  for f in docs/en/*.md; do b=$(basename $f); for l in ptbr es; do [ "$(grep -c '^```' $f)" = "$(grep -c '^```' docs/$l/$b)" ] && [ "$(grep -c '^|' $f)" = "$(grep -c '^|' docs/$l/$b)" ] || echo "MISMATCH $l/$b"; done; done
  ```
  → no output; also `ls docs/en docs/ptbr docs/es` show the same six files.
- [ ] **Step 6: Commit** — `git add -A && git commit -m "Add updating docs (en/ptbr/es)"`.

---

### Task 5: Final verification

- [ ] **Step 1:** `python3.14 -m unittest` → all pass (30).
- [ ] **Step 2:** Clean build twice, `shasum -a 256` of `dist/karman-update.zip` identical; update zip lacks exactly the two `USER_OWNED` files (Task 3 step 3 diff).
- [ ] **Step 3:** `unzip -Z1 dist/karman-update.zip | grep -i -E "lockpick|sigpatch|prod\.keys|title\.keys|\.xci$|\.nsz$"` → no output; and `grep -rn "firmware" switch` shows no bundled firmware (the zip has no `/firmware/` content).
- [ ] **Step 4:** Report honestly: not tested on a console; the release has not been published; the GitHub repo/push is the user's step.
- [ ] **Step 5:** Final whole-branch review as the executing skill requires; fix Critical/Important with TDD.
