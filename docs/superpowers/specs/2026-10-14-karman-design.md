# Karman — Design

Karman is a lite, fast, stable Nintendo Switch CFW pack (SD-card contents), in the vein of Kefir, GNX and vanilla Atmosphere. It ships a curated set of homebrews, ports and tools, with en / ptbr / es support and light customization that costs nothing at boot or runtime.

## Goals
- One command builds a release zip to extract on the SD card.
- Curated, clean, nothing that slows boot.
- Languages: en, ptbr, es, switchable at runtime.
- Reproducible: every build records exactly what it fetched.

## Non-goals (v1)
On-console updater, custom launcher app, per-language zips, sigpatches, and any content the user must supply (keys, firmware, games, ROMs). Karman redistributes none of that.

## Repo layout
```
build.py         stdlib-only build script
manifest.toml    component list
base/            static files copied to the SD root
lang/{en,ptbr,es}/   per-language config overlays (SD-root-relative paths)
lock.json        written by build: version + sha256 per fetched file
test_build.py    smoke test
dist/            output (gitignored)
```

## Component list (`manifest.toml`)
Source types: `github` (repo + asset glob, latest release or pinned tag) and `url` (plain URL, for RetroArch).

| Group | Components |
|---|---|
| Core | Atmosphere (`Atmosphere-NX/Atmosphere`), Hekate + Nyx (`CTCaer/hekate`) |
| Menu / files | Sphaira (`ITotalJustice/sphaira`) |
| Overlays | Ultrahand (`ppkantorski/Ultrahand-Overlay`), ovlSysmodules (`ppkantorski/ovl-sysmodules`), FPSLocker (`masagrator/FPSLocker`), Fizeau (`averne/Fizeau`) |
| Installers | Goldleaf (`XorTroll/Goldleaf`), DBI (`rashevskyv/dbi`) |
| Saves | Checkpoint (`FlagBrew/Checkpoint`), JKSV (`J-D-K/JKSV`) |
| Other tools | NXThemesInstaller (`exelix11/SwitchThemeInjector`), emuiibo (`XorTroll/emuiibo`), sys-ftpd-light (`cathery/sys-ftpd-light`), TegraExplorer (`suchmememanyskill/TegraExplorer`) |
| Ports | DevilutionX (`diasurgical/devilutionX`, `devilutionx-switch.nro`), Perfect Dark (`fgsfdsfgs/perfect_dark`, `pd-arm64-nswitch.zip`, dev build), RetroArch (libretro buildbot `nintendo/switch/libnx/RetroArch.7z`) |

Ports needing user game data (DevilutionX `DIABDAT.MPQ`, Perfect Dark ROM) get an empty data folder and a short README, never the data.

Explicitly excluded: sigpatches, Lockpick_RCM (upstream DMCA-blocked), and stale tools (NX-Shell, nxdumptool, hb-appstore).

## Build pipeline
1. Parse `manifest.toml`.
2. Fetch each component into `.cache/` keyed by URL (rebuilds are fast).
3. Unpack to a staging dir at the destination paths the manifest specifies.
4. Overlay `base/`; apply `lang/en/` as the live default; copy `lang/{en,ptbr,es}/` to `karman/lang/` for the switcher.
5. Write `lock.json` and `dist/karman-<version>.zip`.

Failure is loud and total: an asset glob matching zero or several files, a download error, or a changed SHA-256 on a pinned entry stops the build, names the component, and produces no zip.

## Runtime language switching
- Hekate/Nyx has no language setting, so the switcher does not touch it.
- Overlays contain config only, never binaries. v1 covers Ultrahand (`/config/ultrahand/config.ini`, section `[ultrahand]`, key `default_lang`, values `en` / `pt` / `es`).
- The build generates an Ultrahand package (`/switch/.packages/Karman/package.ini`) with one section per language; each section `copy`s that language's overlay files from `/karman/lang/<xx>/` over the live paths. No payload reboot.
- Zero boot-time cost; code runs only when the user switches.
- Known limit: whole-file copy resets Ultrahand's other settings (key combo, theme).
- Sphaira, DBI, Goldleaf, Checkpoint, JKSV and games follow the Switch system language. Add overlays for them only after their config keys are verified.

## Docs
`docs/{en,ptbr,es}/`: how-to (install), format SD card (Windows, Linux, macOS), emuMMC, customization, languages. Plus a top-level `README.md`.

## Requirements
Python 3.11+ (`tomllib`), stdlib only. `tar` for the one `.7z` (RetroArch).

## Testing
- `test_build.py` builds from a local fixture manifest (no network) and asserts: expected paths in the zip, all three language overlays present, `lock.json` written, and a zero-match glob fails the build.
- One real build is run and its zip listing inspected as the end-to-end check.

## Open items (resolve in implementation)
- Exact Hekate mechanism for the language-switch entries (`hekate_ipl.ini` payload/`.ini` capability vs. a small helper).
- Which per-app configs are actually switchable (see above).
- Version scheme for `karman-<version>.zip` (default: date-based `YYYY.MM.DD`).
