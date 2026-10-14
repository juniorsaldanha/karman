# Atualizando o Karman

## No console (sem computador)
1. Conecte o Switch ao Wi-Fi.
2. Abra o **Ultrahand** (ZL + ZR + D-Pad para baixo) → o pacote **Karman** → **Update Karman (reboot after)**.
3. Aguarde o download e a extração terminarem.
4. **Reinicie** o console (pelo Hekate) para que os novos arquivos do Atmosphere e do Hekate sejam aplicados.

A atualização baixa o `karman-update.zip` da última release de `juniorsaldanha/karman` e o extrai por cima do cartão SD. Ela **não** mexe no seu menu de boot (`bootloader/hekate_ipl.ini`) nem nas configurações do Ultrahand (`config/ultrahand/config.ini`), então suas personalizações e o idioma escolhido continuam. Para ver o que está instalado, abra o `karman/version.txt` no cartão SD.

> **Ainda não testado em um console.** Não verificado: se o arquivo de ~120 MB é extraído de forma confiável pelo Ultrahand, quanto tempo leva, e se sobrescrever os arquivos do próprio Ultrahand enquanto o overlay roda é seguro. Guarde no PC o último `karman-<versão>.zip` completo que funcionou, como plano B. Não há como desfazer.

Se algo falhar, atualize pelo computador: extraia o `karman-<versão>.zip` completo por cima do cartão ([como fazer](how-to.md)).

## Firmware
O Karman não inclui firmware nem tem uma fonte de firmware. Se você definir `firmware_url` (abaixo), o pacote ganha a entrada **Download firmware (then open Daybreak)**: ela baixa o seu zip para `/firmware/` e depois você abre o **Daybreak** (`switch/daybreak.nro`) e instala. Caso contrário, copie você mesmo os arquivos de firmware para `/firmware/`. Use apenas arquivos em que você confia: o Karman não garante a URL.

## Publicando uma release (para quem mantém o projeto)
1. Gere: `GITHUB_TOKEN=$(gh auth token) python3 build.py --version 1.2.0` → `dist/karman-1.2.0.zip` e `dist/karman-update.zip`.
2. Publique os dois arquivos (o asset de atualização **precisa** se chamar `karman-update.zip`):
   ```sh
   gh release create v1.2.0 dist/karman-1.2.0.zip dist/karman-update.zip --title "Karman 1.2.0" --notes "O que mudou"
   ```
3. Os consoles que rodarem **Update Karman** passam a receber esta release.

As configurações ficam na tabela `[release]` do `manifest.toml`: `repo` (`dono/nome` no GitHub) e `firmware_url` opcional. Sem `repo`, o build omite a entrada de atualização.
