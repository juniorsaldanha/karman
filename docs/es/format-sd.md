# Formatear la tarjeta SD para Switch (Windows, Linux, macOS)

Usa **FAT32** con cualquier tamaño: es la opción más estable y con más soporte. exFAT funciona, pero no se recomienda para CFW. Usa **clústeres de 32 KB** cuando la herramienta te deje elegir.

> **Formatear borra todo lo que hay en la tarjeta.** Haz una copia de seguridad antes y revisa dos veces el nombre del dispositivo antes de ejecutar cualquier comando. Un nombre equivocado borra el disco equivocado.

## Windows
**32 GB o menos:** Explorador de archivos → clic derecho en la tarjeta → **Formatear…** → Sistema de archivos **FAT32**, Tamaño de unidad de asignación **32 kilobytes**, marca **Formato rápido** → Iniciar.

**Más de 32 GB:** Windows se niega a formatear en FAT32. Elige una opción:
- Usa un formateador FAT32 como **guiformat** (pon *Allocation unit size* en 32768 y *Volume label* en `KARMAN`), o
- Formatea desde Linux o macOS (abajo), o
- Pon la tarjeta en la Switch, entra en Hekate y usa **Nyx → Tools → Partition SD Card** (reparticiona y formatea toda la tarjeta, incluida una partición opcional de emuMMC).

Verifica: abre el **Símbolo del sistema** y ejecuta `chkdsk X:` (cambia `X:`). Debe mostrar `File system is FAT32` y `32,768 bytes in each allocation unit` (la salida puede aparecer en español, según el sistema).

## Linux
1. Encuentra la tarjeta: `lsblk -o NAME,SIZE,MODEL,TRAN,MOUNTPOINT`. Identifícala por el tamaño, p. ej. `/dev/sdX` (**no** el disco del sistema).
2. Desmonta: `sudo umount /dev/sdX1`
3. ¿Tarjeta en blanco, sin tabla de particiones? Crea una: `sudo parted /dev/sdX --script mklabel msdos mkpart primary fat32 1MiB 100%`
4. Formatea: `sudo mkfs.vfat -F 32 -s 64 -n KARMAN /dev/sdX1` (`-s 64` = 64 sectores × 512 B = clústeres de 32 KB)

Verifica: `sudo fsck.vfat -v /dev/sdX1 | grep -E "bytes per cluster|FAT"` debe mostrar `32768 bytes per cluster`.

## macOS (Darwin)
1. Encuentra la tarjeta: `diskutil list external` e identifícala por el tamaño, p. ej. `/dev/disk4` (**no** el disco interno).
2. Borra como FAT32 con tabla MBR: `diskutil eraseDisk FAT32 KARMAN MBRFormat /dev/disk4`
3. Opcional, forzar clústeres de 32 KB: `diskutil unmountDisk /dev/disk4 && sudo newfs_msdos -F 32 -c 64 -v KARMAN /dev/rdisk4s1 && diskutil mount /dev/disk4s1`

Verifica: `diskutil info /dev/disk4s1 | grep -E "File System|Volume Name"` → `MS-DOS FAT32`, `KARMAN`.

## Después de formatear
Extrae el zip de Karman en la raíz de la tarjeta y sigue con el [cómo hacerlo](how-to.md). Si quieres un emuMMC en partición, decídelo ahora: requiere particionar la tarjeta (mira [emuMMC](emummc.md)).
