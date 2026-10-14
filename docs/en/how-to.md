# How to install Karman

## You need
- A Switch that can enter **RCM** (unpatched Erista, or a Mariko with a modchip). Patched consoles can't use this method.
- A way to inject a payload into RCM (a dongle, or a jig plus a USB cable and an injector app).
- A microSD card (64 GB or more recommended; emuMMC needs about 30 GB on its own).
- A PC or Mac to extract the zip.
- The latest `karman-<version>.zip` (built with `python3 build.py`, see the README).

Karman contains **no** keys, firmware, games or sigpatches. Bring only your own.

## Steps
1. **Back up the SD card**, then [format it as FAT32](format-sd.md).
2. **Extract the zip to the root of the SD card.** Merge folders if asked. The card root must contain `atmosphere/`, `bootloader/`, `switch/`, `config/`, `hbmenu.nro` and `hekate_ctcaer_<version>.bin`. A single extra folder around them (like `karman-1.0/atmosphere/…`) is the most common mistake.
3. Put the Switch in RCM and **inject `hekate_ctcaer_<version>.bin`** (the file at the SD root of the zip; keep a copy on your PC for injection).
4. Hekate's menu appears. **Before the first CFW boot, [create an emuMMC](emummc.md)** (recommended), and back up your system NAND.
5. Choose **Karman (emuMMC)** (or **Karman (SysNAND)** if you know why). **Stock SysNAND** boots without CFW.
6. The console boots into Horizon with Atmosphere running.

## Using it
- **Homebrew menu:** hold **R** while launching a game (or open the Album) to start the homebrew menu; **Sphaira** is the main launcher. Launching the Album with no game open also works.
- **Overlays (Ultrahand):** press **ZL + ZR + D-Pad Down** at any time. Overlays include FPSLocker, Fizeau, system modules, emuiibo and the **Karman** package (language switch).
- **Install games/updates you own:** Goldleaf or DBI.
- **Saves:** Checkpoint or JKSV. **FTP:** sys-ftpd-light (toggle it from the Ultrahand sysmodules overlay).
- **Firmware update:** Daybreak (`switch/daybreak.nro`) using firmware files you supply.
- **Ports:** DevilutionX needs `DIABDAT.MPQ` in its folder; Perfect Dark needs your ROM in `switch/perfectdark/data/`; RetroArch needs cores via *Online Updater → Core Downloader*.

## Updating Karman
On the console, no computer needed: see [updating](updating.md). From a computer: download or build a newer zip and extract it over the card (overwrite). Your saves, emuMMC and games are untouched. Re-extract also resets files Karman manages (`bootloader/hekate_ipl.ini`, Ultrahand's `config.ini`); keep your own tweaks in `base/` ([customize](customize.md)) and rebuild instead.

## Troubleshooting
| Problem | Fix |
|---|---|
| Black screen after choosing Karman | Wrong extract nesting, or missing `atmosphere/package3`. Re-extract to the card root. |
| `emuMMC` entry shows an error | emuMMC isn't created or enabled yet: [create it](emummc.md). |
| Hekate can't see the SD | Re-seat the card; reformat as FAT32 ([guide](format-sd.md)). |
| Atmosphere error after a firmware update | Update Karman to a build that supports that firmware version. |
| Nothing happens in RCM | Check the jig/dongle, the cable, and that the injector shows the payload sent. |
