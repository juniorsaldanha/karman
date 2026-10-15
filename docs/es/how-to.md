# Cómo instalar Karman

## Qué necesitas
- Una Switch que entre en **RCM** (Erista sin parchear, o Mariko con modchip). Las consolas parcheadas no sirven para este método.
- Una forma de inyectar un payload en RCM (un dongle, o un jig con cable USB y una app inyectora).
- Una tarjeta microSD (se recomiendan 64 GB o más; solo el emuMMC ya usa unos 30 GB).
- Un PC o Mac para extraer el zip.
- El `karman-<versión>.zip` más reciente (generado con `python3 build.py`, mira el README).

Karman **no** incluye claves, firmware, juegos ni sigpatches. Usa solo los tuyos.

## Pasos
1. **Haz una copia de seguridad de la tarjeta SD** y luego [formatéala en FAT32](format-sd.md).
2. **Extrae el zip en la raíz de la tarjeta SD.** Si te lo pide, combina las carpetas. La raíz debe contener `atmosphere/`, `bootloader/`, `switch/`, `config/`, `hbmenu.nro` y `hekate_ctcaer_<versión>.bin`. El error más común es una carpeta extra alrededor (como `karman-1.0/atmosphere/…`).
3. Pon la Switch en RCM e **inyecta `hekate_ctcaer_<versión>.bin`** (archivo en la raíz del zip; guarda una copia en el PC para inyectarlo). **Modchip** (Picofly, HWFLY…): no hay nada que inyectar; el zip también pone Hekate en `payload.bin` (con un `boot.ini`), que el chip arranca solo.
4. Aparece el menú de Hekate. **Antes del primer arranque con CFW, [crea un emuMMC](emummc.md)** (recomendado) y haz una copia de seguridad de la NAND del sistema.
5. Elige **Karman (emuMMC)** (o **Karman (SysNAND)** si sabes por qué). **Stock SysNAND** arranca sin CFW.
6. La consola arranca en Horizon con Atmosphere funcionando.

## Uso
- **Menú de homebrew:** mantén **R** al abrir un juego (o abre el Álbum sin mantener R) para iniciar el menú de homebrew; **Sphaira** es el lanzador principal. Abrir el Álbum sin ningún juego abierto también funciona.
- **Overlays (Ultrahand):** pulsa **ZL + ZR + cruceta abajo** en cualquier momento. Incluyen FPSLocker, Fizeau, sysmodules, emuiibo y el paquete **Karman** (cambio de idioma).
- **Reiniciar / apagar:** Ultrahand → paquete **Karman** → *Reboot to boot entry*, *Reboot to Hekate*, *Reboot to USB mass storage*, *Shut down*.
- **Instalar juegos/actualizaciones que posees:** Goldleaf o DBI.
- **Partidas guardadas:** Checkpoint o JKSV. **FTP:** sys-ftpd-light (actívalo desde el overlay de sysmodules de Ultrahand).
- **Actualizar el firmware:** Daybreak (`switch/daybreak.nro`) con archivos de firmware que tú proporcionas.
- **Ports:** DevilutionX necesita `DIABDAT.MPQ` en su carpeta; Perfect Dark necesita tu ROM en `switch/perfectdark/data/`; RetroArch necesita cores desde *Online Updater → Core Downloader*.

## Actualizar Karman
En la consola, sin ordenador: mira [actualizando](updating.md). Desde un ordenador: descarga o genera un zip más nuevo y extráelo sobre la tarjeta (sobrescribiendo). Tus partidas, emuMMC y juegos no se tocan. Volver a extraer también restablece los archivos que gestiona Karman (`bootloader/hekate_ipl.ini`, el `config.ini` de Ultrahand); pon tus ajustes en `base/` ([personalizar](customize.md)) y vuelve a generar.

## Solución de problemas
| Problema | Solución |
|---|---|
| Pantalla negra al elegir Karman | Extracción anidada o falta `atmosphere/package3`. Vuelve a extraer en la raíz de la tarjeta. |
| La entrada `emuMMC` muestra un error | El emuMMC aún no está creado/activado: [créalo](emummc.md). |
| Hekate no ve la SD | Reinserta la tarjeta; reformatea en FAT32 ([guía](format-sd.md)). |
| Error de Atmosphere tras actualizar el firmware | Actualiza Karman a una versión compatible con ese firmware. |
| No pasa nada en RCM | Revisa el jig/dongle, el cable y que el inyector confirme el envío del payload. |
