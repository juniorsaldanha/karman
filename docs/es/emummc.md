# emuMMC (emuNAND)

Un **emuMMC** es una copia de la NAND del sistema de tu Switch guardada en la tarjeta SD. Ejecutas el CFW Atmosphere desde la copia y dejas la NAND real (SysNAND) limpia. Es la forma recomendada de usar Karman.

Karman incluye dos entradas de arranque:
- **Karman (emuMMC)**: usa `emummcforce=1`. Si no hay ningún emuMMC activo, se detiene con un error en lugar de arrancar la SysNAND sin avisar.
- **Karman (SysNAND)**: CFW en la NAND real. Solo si sabes por qué.

## 1. Haz una copia de seguridad primero
En Hekate ve a **Nyx → Tools → Backup eMMC**: respalda **eMMC BOOT0 & BOOT1** (contiene el PRODINFO, los datos de calibración únicos de tu consola) y **eMMC RAW GPP**. Copia el respaldo de la tarjeta SD a tu PC y guárdalo bien. Un PRODINFO perdido no se puede recrear.

## 2. Crea el emuMMC
Necesitas unos **30 GB libres** (más para una copia completa). Elige un tipo.

### En partición (más rápido, recomendado para tarjetas grandes)
Usa una partición raw dedicada. **Esto reparticiona y borra la tarjeta SD**, así que respalda los archivos antes.
1. **Nyx → Tools → Partition SD Card**.
2. Arrastra el control para reservar el tamaño del emuMMC (al menos ~30 GB) y deja el resto como partición FAT32.
3. Inicia. Luego restaura tus archivos (vuelve a extraer el zip de Karman).
4. **Nyx → emuMMC → Create emuMMC → SD Partition** y sigue las indicaciones. Espera a que termine la copia.

### En archivos (más simple, sin reparticionar)
Guarda el emuMMC como archivos en la partición FAT32, en partes de 4 GB.
1. **Nyx → emuMMC → Create emuMMC → SD File**.
2. Sigue las indicaciones para copiar la SysNAND y espera a que termine.

Después, **Nyx → emuMMC → Change emuMMC** muestra y selecciona el activo. Arranca **Karman (emuMMC)**.

## 3. Mantenlo sin conexión
Una consola con CFW que se conecta a los servidores de Nintendo corre riesgo de baneo. Karman incluye `atmosphere/hosts/emummc.txt`, que bloquea todo host `*nintendo*` en el emuMMC (vale solo para el emuMMC, no para la SysNAND):

```
127.0.0.1 *nintendo*
```

Efectos secundarios: la eShop y las funciones en línea de Nintendo no funcionan en el emuMMC, y el Wi-Fi puede indicar fallo en la prueba de conexión (las funciones de red de los homebrews siguen funcionando). Borra el archivo para conectarte con el emuMMC, bajo tu propio riesgo. Una actualización completa desde un ordenador restaura el archivo; la actualización en la consola también. Usa la SysNAND original (sin CFW) para todo lo que sea en línea. No copies partidas ni cuentas entre las dos sin entender las consecuencias.

## 4. Actualizar el firmware dentro del emuMMC
Arranca **Karman (emuMMC)**, abre **Daybreak** (`switch/daybreak.nro`), apúntalo a una carpeta con los archivos de firmware que **tú proporcionas** (Karman no incluye firmware) y elige la opción de instalar. Tras actualizar el firmware, actualiza también Karman (Atmosphere debe ser compatible con ese firmware).

## Solución de problemas
| Problema | Solución |
|---|---|
| "emuMMC not found/enabled" | Créalo (paso 2), o elige **Karman (SysNAND)** conscientemente. |
| Falta de espacio | Libera espacio o usa una tarjeta más grande; el de archivos necesita ~30 GB libres. |
| Arranca en la versión original del firmware | Revisa la entrada: **Stock SysNAND** no carga CFW. |
