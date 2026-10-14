# Format the SD card for Switch (Windows, Linux, macOS)

Use **FAT32** at any size: it's the most stable and widest supported choice. exFAT works but isn't recommended for CFW. Use **32 KB clusters** where the tool lets you choose.

> **Formatting erases everything on the card.** Back it up first, and double-check the device name before you run any command. A wrong device name erases the wrong disk.

## Windows
**32 GB or smaller:** File Explorer → right-click the card → **Format…** → File system **FAT32**, Allocation unit size **32 kilobytes**, tick **Quick Format** → Start.

**Larger than 32 GB:** Windows refuses to format FAT32. Choose one:
- Use a FAT32 formatter such as **guiformat** (set *Allocation unit size* to 32768, *Volume label* `KARMAN`), or
- Format from Linux or macOS (below), or
- Put the card in the Switch, boot Hekate, and use **Nyx → Tools → Partition SD Card** (this repartitions and formats the whole card, including an optional emuMMC partition).

Verify: open **Command Prompt** and run `chkdsk X:` (replace `X:`). It must show `File system is FAT32` and `32,768 bytes in each allocation unit`.

## Linux
1. Find the card: `lsblk -o NAME,SIZE,MODEL,TRAN,MOUNTPOINT`. Identify it by size, e.g. `/dev/sdX` (**not** your system disk).
2. Unmount: `sudo umount /dev/sdX1`
3. Blank card with no partition table? Create one: `sudo parted /dev/sdX --script mklabel msdos mkpart primary fat32 1MiB 100%`
4. Format: `sudo mkfs.vfat -F 32 -s 64 -n KARMAN /dev/sdX1` (`-s 64` = 64 sectors × 512 B = 32 KB clusters)

Verify: `sudo fsck.vfat -v /dev/sdX1 | grep -E "bytes per cluster|FAT"` should show `32768 bytes per cluster`.

## macOS (Darwin)
1. Find the card: `diskutil list external` and identify it by size, e.g. `/dev/disk4` (**not** your internal disk).
2. Erase as FAT32 with an MBR table: `diskutil eraseDisk FAT32 KARMAN MBRFormat /dev/disk4`
3. Optional, force 32 KB clusters: `diskutil unmountDisk /dev/disk4 && sudo newfs_msdos -F 32 -c 64 -v KARMAN /dev/rdisk4s1 && diskutil mount /dev/disk4s1`

Verify: `diskutil info /dev/disk4s1 | grep -E "File System|Volume Name"` → `MS-DOS FAT32`, `KARMAN`.

## After formatting
Extract the Karman zip to the card root and continue with the [how-to](how-to.md). If you want a partition-based emuMMC, decide now: it requires partitioning the card (see [emuMMC](emummc.md)).
