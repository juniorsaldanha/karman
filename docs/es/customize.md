# Personalizar Karman

Karman está hecho de unos pocos archivos simples. Personalízalo editándolos y volviendo a generar (`python3 build.py`). Tus archivos en `base/` se copian **al final**, así que tienen prioridad sobre los archivos originales.

## Cambiar lo que incluye el paquete: `manifest.toml`
Cada `[[component]]` es algo que se descarga:

```toml
[[component]]
name  = "checkpoint"                 # aparece en los errores y en lock.json
source = "github"                    # github | url
repo  = "FlagBrew/Checkpoint"        # solo para github
asset = "Checkpoint.nro"             # glob; debe coincidir con exactamente un asset de la release
dest  = "switch/Checkpoint"          # carpeta relativa a la raíz de la SD
```

| Clave | Significado |
|---|---|
| `pin = "v5.3.0"` | Usa esa etiqueta de release en lugar de la más reciente |
| `sha256 = "…"` | Falla el build si los bytes descargados son distintos |
| `kind` | `zip` (por defecto para `.zip`), `7z`, `file` (copia tal cual) |
| `rename` | Nuevo nombre de archivo para `kind = "file"` |
| `strip = 1` | Quita N carpetas iniciales dentro de un zip |
| `exclude = ["…/*"]` | Omite los archivos que coincidan con esos globs |
| `url` | URL de descarga directa (con `source = "url"`) |

Para **quitar** algo, borra su bloque. Para **añadir**, copia un bloque; ejecuta `python3 build.py` y revisa `lock.json` / el listado del zip para ver dónde quedaron los archivos.

## Menú de arranque: `base/bootloader/hekate_ipl.ini`
- `bootwait=3`: segundos manteniendo **VOL−** para abrir el menú (0 = omite el menú y el logo).
- `autoboot=N` / `autoboot_list=0`: arranca la entrada N automáticamente (0 = menú). Déjalo desactivado hasta estar seguro de que todo funciona.
- Renombra entradas editando el `[Nombre de sección]`; añade un logo con `logopath=bootloader/bootlogo.bmp` más tu `bootlogo.bmp` en `base/bootloader/`.
- Todas las claves están en el [README de Hekate](https://github.com/CTCaer/hekate) (sección *hekate_ipl.ini*).

## Aspecto de Nyx: `bootloader/nyx.ini`
Crea `base/bootloader/nyx.ini`:

```ini
[config]
themecolor=167
themebg=2d2d2d
homescreen=0
```

## Overlays y temas (Ultrahand)
Abre Ultrahand (**ZL+ZR+cruceta abajo**) → Settings para elegir **tema**, **fondo**, **sonidos** y **combinación de botones**. Viven en `/config/ultrahand/`; para distribuir tu elección, pon los archivos en `base/config/ultrahand/` y vuelve a generar. Ojo: el cambio de idioma sobrescribe `config.ini` ([idiomas](languages.md)).

## Añade tus propios archivos
Todo lo que esté en `base/` termina en la raíz de la SD: tus homebrews NRO, temas, trucos (`atmosphere/contents/<titleid>/cheats/`), etc.

## Añadir o cambiar una capa de idioma
`lang/<xx>/…` replica la raíz de la SD; contiene solo archivos de configuración. Para cubrir otra app, añade su archivo de configuración verificado en cada `lang/<xx>/`. El build lo agrega solo al paquete Karman de Ultrahand. Para añadir un idioma nuevo, crea una carpeta y una entrada en `LANGS` en `build.py`.

## Mantenlo rápido
- Cada sysmodule y overlay usa RAM y a veces tiempo de arranque. Quita lo que no uses.
- Deja `autoboot` desactivado mientras pruebas; una entrada mala con arranque automático es más difícil de recuperar.
- No incluyas datos grandes (ROMs, cores, bases de datos). Los cores de RetroArch vienen del Online Updater a propósito.
