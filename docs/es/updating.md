# Actualizar Karman

## En la consola (sin ordenador)
1. Conecta la Switch al Wi-Fi.
2. Abre **Ultrahand** (ZL + ZR + cruceta abajo) → el paquete **Karman** → **Update Karman (reboot after)**.
3. Espera a que terminen la descarga y la extracción.
4. **Reinicia** la consola (desde Hekate) para que se apliquen los nuevos archivos de Atmosphere y Hekate.

La actualización descarga `karman-update.zip` de la última release de `juniorsaldanha/karman` y lo extrae sobre la tarjeta SD. **No** toca tu menú de arranque (`bootloader/hekate_ipl.ini`) ni los ajustes de Ultrahand (`config/ultrahand/config.ini`), así que tus personalizaciones y el idioma elegido se conservan. Para ver qué tienes instalado, abre `karman/version.txt` en la tarjeta SD.

> **Aún no probado en una consola.** Sin verificar: si el archivo de ~120 MB se extrae de forma fiable con Ultrahand, cuánto tarda, y si es seguro sobrescribir los archivos del propio Ultrahand mientras su overlay está en marcha. Guarda en el PC el último `karman-<versión>.zip` completo que funcionó, como plan B. No hay forma de deshacer.

Si algo falla, actualiza desde un ordenador: extrae el `karman-<versión>.zip` completo sobre la tarjeta ([cómo hacerlo](how-to.md)).

## Firmware
Karman no incluye firmware ni tiene una fuente de firmware. Si defines `firmware_url` (abajo), el paquete añade la entrada **Download firmware (then open Daybreak)**: descarga tu zip en `/firmware/` y luego abres **Daybreak** (`switch/daybreak.nro`) para instalarlo. Si no, copia tú mismo los archivos de firmware en `/firmware/`. Usa solo archivos en los que confíes: Karman no garantiza la URL.

## Publicar una release (para quien mantiene el proyecto)
1. Genera: `GITHUB_TOKEN=$(gh auth token) python3 build.py --version 1.2.0` → `dist/karman-1.2.0.zip` y `dist/karman-update.zip`.
2. Publica los dos archivos (el asset de actualización **debe** llamarse `karman-update.zip`):
   ```sh
   gh release create v1.2.0 dist/karman-1.2.0.zip dist/karman-update.zip --title "Karman 1.2.0" --notes "Qué cambió"
   ```
3. Las consolas que ejecuten **Update Karman** recibirán esta release.

Los ajustes están en la tabla `[release]` de `manifest.toml`: `repo` (`dueño/nombre` en GitHub) y `firmware_url` opcional. Sin `repo`, el build omite la entrada de actualización.
