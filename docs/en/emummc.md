# emuMMC (emuNAND)

An **emuMMC** is a copy of your Switch's system NAND stored on the SD card. You run Atmosphere CFW from the copy and leave the real system NAND (SysNAND) clean. It's the recommended way to use Karman.

Karman ships two boot entries:
- **Karman (emuMMC)**: uses `emummcforce=1`. If no emuMMC is enabled it stops with an error instead of silently booting SysNAND.
- **Karman (SysNAND)**: CFW on the real NAND. Only if you know why.

## 1. Back up first
In Hekate go to **Nyx → Tools → Backup eMMC**: back up **eMMC BOOT0 & BOOT1** (it contains PRODINFO, your console's unique calibration data) and **eMMC RAW GPP**. Copy the backup off the SD card to your PC and keep it safe. A lost PRODINFO can't be recreated.

## 2. Create the emuMMC
You need about **30 GB free** (more for a full copy). Choose one type.

### Partition-based (faster, recommended for large cards)
Uses a dedicated raw partition. **This repartitions the SD card and erases it**, so back up the files first.
1. **Nyx → Tools → Partition SD Card**.
2. Drag the slider to reserve the emuMMC size (at least ~30 GB), leave the rest as the FAT32 partition.
3. Start. Then restore your files (re-extract the Karman zip).
4. **Nyx → emuMMC → Create emuMMC → SD Partition** and follow the prompts. Wait for the copy.

### File-based (simpler, no repartition)
Stores the emuMMC as files on the FAT32 partition, in 4 GB parts.
1. **Nyx → emuMMC → Create emuMMC → SD File**.
2. Follow the prompts to copy SysNAND and wait for it to finish.

Afterwards **Nyx → emuMMC → Change emuMMC** shows and selects the active one. Boot **Karman (emuMMC)**.

## 3. Keep it offline
A CFW console that connects to Nintendo's servers risks a ban. Karman ships `atmosphere/hosts/emummc.txt`, which blocks every `*nintendo*` host for the emuMMC (it applies to the emuMMC only, not to SysNAND):

```
127.0.0.1 *nintendo*
```

Side effects: the eShop and Nintendo online features won't work in the emuMMC, and Wi-Fi may report a failed connection test (homebrew network features still work). Delete the file to go online with the emuMMC, at your own risk. A full update from a computer restores the file; the on-console update does too. Use the stock (non-CFW) SysNAND for anything online. Don't copy saves or accounts between the two without understanding the consequences.

## 4. Updating firmware inside the emuMMC
Boot **Karman (emuMMC)**, open **Daybreak** (`switch/daybreak.nro`), point it at a folder with the firmware files **you supply** (Karman doesn't include firmware), choose the install option. After a firmware update, update Karman too (Atmosphere must support that firmware).

## Troubleshooting
| Problem | Fix |
|---|---|
| "emuMMC not found/enabled" | Create it (step 2), or pick **Karman (SysNAND)** knowingly. |
| Not enough space | Free space or use a bigger card; file-based needs ~30 GB free. |
| Boots to stock firmware version | Check the entry: **Stock SysNAND** doesn't load CFW. |
