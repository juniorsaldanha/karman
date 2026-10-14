# Updating Karman

## On the console (no computer)
1. Connect the Switch to Wi-Fi.
2. Open **Ultrahand** (ZL + ZR + D-Pad Down) → the **Karman** package → **Update Karman (reboot after)**.
3. Wait for the download and extraction to finish.
4. **Reboot** the console (through Hekate) so the new Atmosphere and Hekate files apply.

The update downloads `karman-update.zip` from the latest release of `juniorsaldanha/karman` and extracts it over the SD card. It deliberately does **not** replace four files you may have edited: your boot menu (`bootloader/hekate_ipl.ini`), Ultrahand's `config/ultrahand/config.ini` (so your chosen language stays), `config/sys-ftpd/config.ini` and `config/Fizeau/config.ini`. Everything else Karman manages is replaced, including Ultrahand's other files and the Karman package itself, and a sysmodule you switched off may come back on. To see what you have installed, open `karman/version.txt` on the SD card.

> **Not tested on a console yet.** Unverified: whether the ~120 MB archive extracts reliably through Ultrahand, how long it takes, and whether overwriting Ultrahand's own files while its overlay runs is safe. Keep your last good full `karman-<version>.zip` on your PC as a fallback. There is no rollback.

If anything fails, update from a computer: extract the full `karman-<version>.zip` over the card ([how-to](how-to.md)).

## Good to know
- **First time:** packs installed before the updater existed have no *Update Karman* entry. Do one full install from a computer first ([how-to](how-to.md)).
- **Boot menu changes:** because `hekate_ipl.ini` is kept, new boot entries in a release don't reach you. Extract the full zip or copy the entries by hand.
- **Always the latest:** it never compares versions, so it re-downloads about 120 MB every time and can't be used to go back.
- **Why reboot:** Atmosphere and Hekate files only take effect at boot; until then you are running the old ones.

## Firmware
Karman ships no firmware and has no firmware source. If you set `firmware_url` (below), the package gets a **Download firmware (then open Daybreak)** entry: it downloads your zip to `/firmware/`, then you open **Daybreak** (`switch/daybreak.nro`) and install it. Otherwise copy the firmware files to `/firmware/` yourself. Clear `/firmware/` first so versions don't mix, and make sure the zip holds the firmware files at its top level, not inside a folder. Only use files you trust: Karman does not vouch for the URL.

## Publishing a release (for the maintainer)
1. Build: `GITHUB_TOKEN=$(gh auth token) python3 build.py --version 1.2.0` → `dist/karman-1.2.0.zip` and `dist/karman-update.zip`.
2. Publish both files (the update asset **must** be named `karman-update.zip`):
   ```sh
   gh release create v1.2.0 dist/karman-1.2.0.zip dist/karman-update.zip --title "Karman 1.2.0" --notes "What changed"
   ```
3. Consoles that run **Update Karman** now get this release.

Settings live in the `[release]` table of `manifest.toml`: `repo` (GitHub `owner/name`) and optional `firmware_url`. With no `repo`, the build omits the update entry.
