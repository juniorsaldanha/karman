# Karman

A lite, fast and stable Nintendo Switch CFW pack, in the vein of Kefir, GNX and vanilla Atmosphere. Clean boot menu, a curated set of homebrews, ports and tools, and **en / ptbr / es** support, with no customization that costs boot time or runtime speed.

Karman is a **build system**: it downloads the latest upstream releases, applies Karman's configuration and translations, and writes one zip to extract on the SD card. No binaries are committed to this repo.

## What's inside

| Group | Components |
|---|---|
| Core | Atmosphere, Hekate + Nyx |
| Menu / files | Sphaira (plus hbmenu) |
| Overlays | Ultrahand, ovlSysmodules, FPSLocker, Fizeau |
| Installers | Goldleaf, DBI |
| Saves | Checkpoint, JKSV |
| Tools | NXThemesInstaller, emuiibo, sys-ftpd-light, TegraExplorer, Daybreak (from Atmosphere) |
| Ports | DevilutionX, Perfect Dark, RetroArch (frontend; get cores in-app) |

**Not included, by design:** keys, firmware, games, ROMs, sigpatches. Ports that need game data (DevilutionX needs `DIABDAT.MPQ`, Perfect Dark needs your own ROM) get only the folder to put it in.

## Build

Requires Python 3.11+ (standard library only) and `tar`.

```sh
export GITHUB_TOKEN=...        # optional but recommended: avoids GitHub's 60 requests/hour limit
python3 build.py               # -> dist/karman-<YYYY.MM.DD>.zip
python3 build.py --version 1.0 # custom version
python3 -m unittest            # run the tests (no network needed)
```

Each build writes `lock.json` (tag, asset and SHA-256 of every component), so builds are reproducible: the same inputs give a byte-identical zip. A failed build produces no zip and names the failing component.

## Install

1. [Format the SD card](docs/en/format-sd.md) (FAT32).
2. Extract the zip to the **root** of the SD card.
3. Follow the [how-to](docs/en/how-to.md).

## Docs

| | English | Português (BR) | Español |
|---|---|---|---|
| Install | [how-to](docs/en/how-to.md) | [como fazer](docs/ptbr/how-to.md) | [cómo hacerlo](docs/es/how-to.md) |
| Format the SD card | [format-sd](docs/en/format-sd.md) | [formatar](docs/ptbr/format-sd.md) | [formatear](docs/es/format-sd.md) |
| emuMMC (emuNAND) | [emummc](docs/en/emummc.md) | [emummc](docs/ptbr/emummc.md) | [emummc](docs/es/emummc.md) |
| Customize | [customize](docs/en/customize.md) | [personalizar](docs/ptbr/customize.md) | [personalizar](docs/es/customize.md) |
| Languages | [languages](docs/en/languages.md) | [idiomas](docs/ptbr/languages.md) | [idiomas](docs/es/languages.md) |

## Layout

```
build.py          the whole build (stdlib only)
manifest.toml     component list: edit it to add/remove things
base/             static files copied to the SD root (hekate_ipl.ini, ...)
lang/{en,ptbr,es} per-language config overlays
test_build.py     tests
docs/             guides
```

## Legal

Karman redistributes nothing itself; it fetches public releases of open homebrew. You are responsible for using it only with a console and games you own. Nintendo Switch is a trademark of Nintendo; Karman is not affiliated with Nintendo.
