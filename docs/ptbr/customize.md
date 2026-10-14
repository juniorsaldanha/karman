# Personalizar o Karman

O Karman é feito de alguns arquivos simples. Personalize editando-os e gerando de novo (`python3 build.py`). Seus arquivos em `base/` são copiados **por último**, então têm prioridade sobre os arquivos originais.

## Mudar o que vai no pacote: `manifest.toml`
Cada `[[component]]` é uma coisa a baixar:

```toml
[[component]]
name  = "checkpoint"                 # aparece nos erros e no lock.json
source = "github"                    # github | url
repo  = "FlagBrew/Checkpoint"        # só para github
asset = "Checkpoint.nro"             # glob; deve casar com exatamente um asset da release
dest  = "switch/Checkpoint"          # pasta relativa à raiz do SD
```

| Chave | Significado |
|---|---|
| `pin = "v5.3.0"` | Usa essa tag de release em vez da mais recente |
| `sha256 = "…"` | Falha o build se os bytes baixados forem diferentes |
| `kind` | `zip` (padrão para `.zip`), `7z`, `file` (copia como está) |
| `rename` | Novo nome de arquivo para `kind = "file"` |
| `strip = 1` | Remove N pastas iniciais dentro de um zip |
| `exclude = ["…/*"]` | Ignora arquivos que casem com esses globs |
| `url` | URL direta de download (com `source = "url"`) |

Para **remover** algo, apague o bloco. Para **adicionar**, copie um bloco; rode `python3 build.py` e confira o `lock.json` / a lista do zip para ver onde os arquivos caíram.

## Menu de boot: `base/bootloader/hekate_ipl.ini`
- `bootwait=3`: segundos segurando **VOL−** para abrir o menu (0 = pula o menu e o logo).
- `autoboot=N` / `autoboot_list=0`: inicia a entrada N automaticamente (0 = menu). Deixe desligado até ter certeza de que tudo funciona.
- Renomeie entradas editando o `[Nome da seção]`; adicione um logo com `logopath=bootloader/bootlogo.bmp` mais o seu `bootlogo.bmp` em `base/bootloader/`.
- Todas as chaves estão no [README do Hekate](https://github.com/CTCaer/hekate) (seção *hekate_ipl.ini*).

## Aparência do Nyx: `bootloader/nyx.ini`
Crie `base/bootloader/nyx.ini`:

```ini
[config]
themecolor=167
themebg=2d2d2d
homescreen=0
```

## Overlays e temas (Ultrahand)
Abra o Ultrahand (**ZL+ZR+D-Pad para baixo**) → Settings para escolher **tema**, **wallpaper**, **sons** e **combinação de teclas**. Eles ficam em `/config/ultrahand/`; para distribuir sua escolha, coloque os arquivos em `base/config/ultrahand/` e gere de novo. Atenção: a troca de idioma sobrescreve o `config.ini` ([idiomas](languages.md)).

## Adicione seus próprios arquivos
Tudo em `base/` vai para a raiz do SD: seus homebrews NRO, temas, cheats (`atmosphere/contents/<titleid>/cheats/`), etc.

## Adicionar ou mudar uma sobreposição de idioma
`lang/<xx>/…` espelha a raiz do SD; guarda só arquivos de configuração. Para cobrir outro app, adicione o arquivo de configuração verificado dele em cada `lang/<xx>/`. O build o inclui automaticamente no pacote Karman do Ultrahand. Para adicionar um idioma novo, crie uma pasta e uma entrada em `LANGS` no `build.py`.

## Mantenha rápido
- Cada sysmodule e overlay usa RAM e, às vezes, tempo de boot. Remova o que você não usa.
- Deixe o `autoboot` desligado enquanto testa; uma entrada ruim com boot automático é mais difícil de recuperar.
- Não inclua dados grandes (ROMs, cores, bancos de dados). Os cores do RetroArch vêm do Online Updater de propósito.
