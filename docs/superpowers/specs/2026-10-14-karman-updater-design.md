# Karman on-console updater — Design

Extends `2026-10-14-karman-design.md`. Lets a user update Karman from the Switch itself, with no computer.

## Goals
- Update the whole pack from an Ultrahand menu entry: download, extract, reboot.
- Updating never wipes the user's boot menu or Ultrahand settings.
- No new toolchain and no compiled code: the updater is generated Ultrahand package script.
- Optional firmware download that ships with no firmware source of its own.

## Non-goals
Per-component updates, a native libnx app, automatic version comparison, any bundled firmware or firmware mirror, creating the GitHub repo or publishing releases for the user.

## Hosting
GitHub Releases of `juniorsaldanha/karman`. Stable asset URLs:
- `https://github.com/juniorsaldanha/karman/releases/latest/download/karman-update.zip`

No JSON parsing on the console: the asset name is constant, so `releases/latest/download/<name>` always resolves to the newest release.

## Build changes (`build.py`)
1. **Config:** `manifest.toml` gains a top-level table `[release]` with `repo = "juniorsaldanha/karman"` and an optional `firmware_url`. Read by `build.py`; absent `repo` means no update entry is generated.
2. **Two zips per build:**
   - `dist/karman-<version>.zip`: the full pack, as today.
   - `dist/karman-update.zip`: the same file set minus the user-owned files (`USER_OWNED`: `bootloader/hekate_ipl.ini`, `config/ultrahand/config.ini`). Same deterministic writer.
3. **`karman/version.txt`** inside the pack holds the version string, so the user can see what is installed. The build gets the version from `--version`.
4. **Package entries**, generated into `switch/.packages/Karman/package.ini` next to the language sections:
   - `[Update Karman]`: `download <update-url> /config/ultrahand/downloads/karman-update.zip`, `unzip` it into `/config/ultrahand/downloads/karman-update/`, `move` that folder onto `/`, `delete` the temp files, then show a "reboot to apply" message. Wrapped in the same `try:` fallback style as Ultrahand's Easy Installer example.
   - `[Download firmware]`, only when `release.firmware_url` is set: `download <firmware-url>` to the downloads folder, `unzip` into `/firmware/`, `delete` the zip, message pointing the user to Daybreak. The URL is the user's; Karman ships none.
5. **Language entries stay as they are.** Because `karman-update.zip` excludes `config/ultrahand/config.ini`, an update does not reset the chosen language either.

## Publishing (documented, not automated)
`gh release create v<version> dist/karman-<version>.zip dist/karman-update.zip --title ... --notes ...`, documented in the README and a new `docs/{en,ptbr,es}/updating.md`. The agent does not create the repo or push.

## Docs
New `updating.md` in en/ptbr/es (how to update on the console, what is preserved, how to publish a release, how to set a firmware URL, honest limits). Update the README docs table and the existing how-to "Updating Karman" section to point to it.

## Testing (no network)
- `karman-update.zip` is built, is deterministic, and contains every file of the full zip except exactly `USER_OWNED`.
- `karman/version.txt` is present and equals the version.
- `package.ini` contains the update URL for the configured repo, the `download`, `unzip`, `move` and `delete` lines, and no update section when `release.repo` is absent.
- The firmware section appears only when `firmware_url` is set, and contains that exact URL.
- Failure cases: a missing `USER_OWNED` file in the stage is fine (not an error); a malformed `[release]` table (non-string `repo`) fails the build naming the key.
- One real build lists both zips and `karman/version.txt`.

## Known limits (stated in the docs)
- Not run on a console. Unverified: whether Ultrahand's `unzip` handles a ~120 MB archive, how long the update takes, whether overwriting Ultrahand's own files while its overlay is running is safe, and that the exact command syntax (`try:`, `move` onto `/`) behaves as in the Easy Installer example.
- Updating replaces files Karman manages but not user-owned ones; a user who edited other managed files (for example Nyx `nyx.ini` in `base/`) loses those edits unless they rebuild from source.
- No rollback. Users should keep their last good full zip.
- Firmware files come from a URL the user supplies; Karman does not vouch for it.

## Requirements
Unchanged: Python 3.11+, stdlib only.
