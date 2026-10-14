# Customize Karman

Karman is built from a handful of plain files. Customize by editing them and rebuilding (`python3 build.py`). Your files in `base/` are copied **last**, so they win over upstream files.

## Change what's in the pack: `manifest.toml`
Each `[[component]]` is one thing to fetch:

```toml
[[component]]
name  = "checkpoint"                 # shown in errors and lock.json
source = "github"                    # github | url
repo  = "FlagBrew/Checkpoint"        # github only
asset = "Checkpoint.nro"             # glob; must match exactly one release asset
dest  = "switch/Checkpoint"          # SD-root-relative folder
```

| Key | Meaning |
|---|---|
| `pin = "v5.3.0"` | Use that release tag instead of the latest |
| `sha256 = "…"` | Fail the build if the downloaded bytes differ |
| `kind` | `zip` (default for `.zip`), `7z`, `file` (copy as-is) |
| `rename` | New file name for `kind = "file"` |
| `strip = 1` | Drop N leading folders inside a zip |
| `exclude = ["…/*"]` | Skip files matching these globs |
| `url` | Direct download URL (with `source = "url"`) |

To **remove** something, delete its block. To **add**, copy a block; run `python3 build.py` and read `lock.json` / the zip listing to confirm where files landed.

## Boot menu: `base/bootloader/hekate_ipl.ini`
- `bootwait=3`: seconds to hold **VOL−** for the menu (0 = skip the menu and the logo).
- `autoboot=N` / `autoboot_list=0`: boot entry N automatically (0 = menu). Keep it off until you're sure everything works.
- Rename entries by editing the `[Section name]`; add a logo with `logopath=bootloader/bootlogo.bmp` plus your `bootlogo.bmp` in `base/bootloader/`.
- All keys are documented in the [Hekate README](https://github.com/CTCaer/hekate) (section *hekate_ipl.ini*).

## Nyx look: `bootloader/nyx.ini`
Create `base/bootloader/nyx.ini`:

```ini
[config]
themecolor=167
themebg=2d2d2d
homescreen=0
```

## Overlays and themes (Ultrahand)
Open Ultrahand (**ZL+ZR+D-Down**) → Settings to pick a **theme**, **wallpaper**, **sounds** and **key combo**. These live in `/config/ultrahand/`; to ship your choice, put the files in `base/config/ultrahand/` and rebuild. Note: the language switch overwrites `config.ini` ([languages](languages.md)).

## Add your own files
Anything under `base/` ends up at the SD root: your own homebrew NROs, themes, cheats (`atmosphere/contents/<titleid>/cheats/`), etc.

## Add or change a language overlay
`lang/<xx>/…` mirrors the SD root; it holds config files only. To cover another app, add its verified config file under every `lang/<xx>/`. The build then adds it to the Karman Ultrahand package automatically. To add a new language, add a folder and an entry in `LANGS` in `build.py`.

## Keep it fast
- Every sysmodule and overlay uses RAM and sometimes boot time. Remove what you don't use.
- Leave `autoboot` off while testing; a bad entry that auto-boots is harder to recover from.
- Don't ship large data (ROMs, cores, databases). RetroArch cores come from its Online Updater on purpose.
