# Actualizar Karman

## En la consola (sin ordenador)
1. Conecta la Switch al Wi-Fi.
2. Abre **Ultrahand** (ZL + ZR + cruceta abajo) → el paquete **Karman** → **Update Karman (reboot after)**.
3. Primero comprueba la última release. Si ya estás al día, te lo dice; si tu build instalada es **más nueva** que la última release, se niega (protección contra downgrade); si no puede comprobar (sin red, sin release), no cambia nada. Si no, espera a que terminen la descarga y la extracción.
4. **Reinicia** la consola (desde Hekate) para que se apliquen los nuevos archivos de Atmosphere y Hekate.

La actualización descarga `karman-update.zip` de la última release de `juniorsaldanha/karman` y lo extrae sobre la tarjeta SD. Deliberadamente **no** reemplaza cuatro archivos que puedes haber editado: tu menú de arranque (`bootloader/hekate_ipl.ini`), el `config/ultrahand/config.ini` de Ultrahand (así que el idioma elegido se conserva), `config/sys-ftpd/config.ini` y `config/Fizeau/config.ini`. Todo lo demás que gestiona Karman se reemplaza, incluidos los otros archivos de Ultrahand y el propio paquete Karman, y un sysmodule que hayas desactivado puede volver a activarse. Para ver qué tienes instalado, abre `karman/version.ini` en la tarjeta SD (guarda la versión y el número de build de 8 dígitos que compara la comprobación).

> **Aún no probado en una consola.** Sin verificar: la propia comprobación de actualización/downgrade (usa placeholders anidados de Ultrahand y matemática de enteros; está hecha para fallar de forma segura, así que el peor caso es "no se pudo comprobar" o ninguna actualización, nunca una instalación equivocada), si el archivo de ~120 MB se extrae de forma fiable con Ultrahand, cuánto tarda, y si es seguro sobrescribir los archivos del propio Ultrahand mientras su overlay está en marcha. Guarda en el PC el último `karman-<versión>.zip` completo que funcionó, como plan B. No hay forma de deshacer.

Si algo falla, actualiza desde un ordenador: extrae el `karman-<versión>.zip` completo sobre la tarjeta ([cómo hacerlo](how-to.md)).

## Forzar la instalación (bajo tu propio riesgo)
La entrada **Force install latest (may downgrade - at your own risk)** se salta la comprobación: mantén **A** unos 3 segundos y instala la última release aunque sea más antigua que la tuya. Úsala para volver a una release estable o reparar una instalación rota, y recuerda que no hay forma de deshacer. Si dudas, prefiere una instalación completa desde un ordenador.

## Conviene saber
- **Primera vez:** los paquetes instalados antes de que existiera el actualizador no tienen la entrada *Update Karman*. Haz primero una instalación completa desde un ordenador ([cómo hacerlo](how-to.md)).
- **Cambios en el menú de arranque:** como se conserva `hekate_ipl.ini`, las nuevas entradas de arranque de una release no te llegan. Extrae el zip completo o copia las entradas a mano.
- **Por qué reiniciar:** los archivos de Atmosphere y Hekate solo se aplican al arrancar; hasta entonces usas los antiguos.

## Firmware
Karman no incluye firmware ni tiene una fuente de firmware. Si defines `firmware_url` (abajo), el paquete añade la entrada **Download firmware (then open Daybreak)**: descarga tu zip en `/firmware/` y luego abres **Daybreak** (`switch/daybreak.nro`) para instalarlo. Si no, copia tú mismo los archivos de firmware en `/firmware/`. Vacía `/firmware/` antes para no mezclar versiones, y comprueba que el zip trae los archivos de firmware en su raíz, no dentro de una carpeta. Usa solo archivos en los que confíes: Karman no garantiza la URL.

## Publicar una release (para quien mantiene el proyecto)
1. Genera: `GITHUB_TOKEN=$(gh auth token) python3 build.py --version 1.2.0 --build 26101401` → `dist/karman-1.2.0.zip`, `dist/karman-update.zip` y `dist/karman-latest.ini`. El número de build tiene 8 dígitos, `YYMMDDNN` (por defecto: hoy más `01`). ¿Publicas dos veces el mismo día? Sube el `NN` (`26101402`). **Nunca reutilices ni bajes un número de build**: las consolas lo comparan para decidir qué es más nuevo.
2. Publica los tres archivos (los nombres de los assets **deben** seguir siendo `karman-update.zip` y `karman-latest.ini`):
   ```sh
   gh release create v1.2.0 dist/karman-1.2.0.zip dist/karman-update.zip dist/karman-latest.ini --title "Karman 1.2.0" --notes "Qué cambió"
   ```
3. Las consolas que ejecuten **Update Karman** recibirán esta release.

Los ajustes están en la tabla `[release]` de `manifest.toml`: `repo` (`dueño/nombre` en GitHub) y `firmware_url` opcional. Sin `repo`, el build omite la entrada de actualización.
