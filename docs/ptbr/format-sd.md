# Formatar o cartão SD para Switch (Windows, Linux, macOS)

Use **FAT32** em qualquer tamanho: é a opção mais estável e com mais suporte. exFAT funciona, mas não é recomendado para CFW. Use **clusters de 32 KB** quando a ferramenta permitir escolher.

> **Formatar apaga tudo no cartão.** Faça backup antes e confira duas vezes o nome do dispositivo antes de rodar qualquer comando. Um nome errado apaga o disco errado.

## Windows
**32 GB ou menos:** Explorador de Arquivos → botão direito no cartão → **Formatar…** → Sistema de arquivos **FAT32**, Tamanho da unidade de alocação **32 quilobytes**, marque **Formatação rápida** → Iniciar.

**Mais de 32 GB:** o Windows se recusa a formatar em FAT32. Escolha uma opção:
- Use um formatador FAT32 como o **guiformat** (defina *Allocation unit size* como 32768 e *Volume label* como `KARMAN`), ou
- Formate pelo Linux ou macOS (abaixo), ou
- Coloque o cartão no Switch, entre no Hekate e use **Nyx → Tools → Partition SD Card** (reparticiona e formata o cartão inteiro, incluindo uma partição opcional de emuMMC).

Verifique: abra o **Prompt de Comando** e rode `chkdsk X:` (troque `X:`). Deve mostrar `File system is FAT32` e `32,768 bytes in each allocation unit` (a saída pode aparecer em português, dependendo do sistema).

## Linux
1. Encontre o cartão: `lsblk -o NAME,SIZE,MODEL,TRAN,MOUNTPOINT`. Identifique pelo tamanho, ex.: `/dev/sdX` (**não** o disco do sistema).
2. Desmonte: `sudo umount /dev/sdX1`
3. Cartão em branco, sem tabela de partições? Crie uma: `sudo parted /dev/sdX --script mklabel msdos mkpart primary fat32 1MiB 100%`
4. Formate: `sudo mkfs.vfat -F 32 -s 64 -n KARMAN /dev/sdX1` (`-s 64` = 64 setores × 512 B = clusters de 32 KB)

Verifique: `sudo fsck.vfat -v /dev/sdX1 | grep -E "bytes per cluster|FAT"` deve mostrar `32768 bytes per cluster`.

## macOS (Darwin)
1. Encontre o cartão: `diskutil list external` e identifique pelo tamanho, ex.: `/dev/diskN` (**não** o disco interno). Nos comandos abaixo, troque o `N` de `diskN` por esse número.
2. Apague como FAT32 com tabela MBR: `diskutil eraseDisk FAT32 KARMAN MBRFormat /dev/diskN`
3. Opcional, forçar clusters de 32 KB: `diskutil unmountDisk /dev/diskN && sudo newfs_msdos -F 32 -c 64 -v KARMAN /dev/rdiskNs1 && diskutil mount /dev/diskNs1`

Verifique: `diskutil info /dev/diskNs1 | grep -E "File System|Volume Name"` → `MS-DOS FAT32`, `KARMAN`.

## Depois de formatar
Extraia o zip do Karman na raiz do cartão e continue com o [como fazer](how-to.md). Se quiser um emuMMC em partição, decida agora: isso exige particionar o cartão (veja [emuMMC](emummc.md)).
