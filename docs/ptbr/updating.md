# Atualizando o Karman

## No console (sem computador)
1. Conecte o Switch ao Wi-Fi.
2. Abra o **Ultrahand** (ZL + ZR + D-Pad para baixo) → o pacote **Karman** → **Update Karman (reboot after)**.
3. Primeiro ele verifica a última release. Se você já está atualizado, avisa; se a sua build instalada for **mais nova** que a última release, ele recusa (proteção contra downgrade); se não conseguir verificar (sem rede, sem release), não altera nada. Caso contrário, aguarde o download e a extração terminarem.
4. **Reinicie** o console (pelo Hekate) para que os novos arquivos do Atmosphere e do Hekate sejam aplicados.

A atualização baixa o `karman-update.zip` da última release de `juniorsaldanha/karman` e o extrai por cima do cartão SD. Ela deliberadamente **não** substitui quatro arquivos que você pode ter editado: seu menu de boot (`bootloader/hekate_ipl.ini`), o `config/ultrahand/config.ini` do Ultrahand (então o idioma escolhido continua), `config/sys-ftpd/config.ini` e `config/Fizeau/config.ini`. Todo o resto que o Karman gerencia é substituído, incluindo os outros arquivos do Ultrahand e o próprio pacote Karman, e um sysmodule que você desligou pode voltar a ficar ligado. Para ver o que está instalado, abra o `karman/version.ini` no cartão SD (ele guarda a versão e o número de build de 8 dígitos que a verificação compara).

> **Ainda não testado em um console.** Não verificado: a própria verificação de atualização/downgrade (usa placeholders aninhados do Ultrahand e matemática de inteiros; foi feita para falhar de forma segura, então o pior caso é "não foi possível verificar" ou nenhuma atualização, nunca uma instalação errada), se o arquivo de ~120 MB é extraído de forma confiável pelo Ultrahand, quanto tempo leva, e se sobrescrever os arquivos do próprio Ultrahand enquanto o overlay roda é seguro. Guarde no PC o último `karman-<versão>.zip` completo que funcionou, como plano B. Não há como desfazer.

Se algo falhar, atualize pelo computador: extraia o `karman-<versão>.zip` completo por cima do cartão ([como fazer](how-to.md)).

## Forçar a instalação (por sua conta e risco)
A entrada **Force install latest (may downgrade - at your own risk)** pula a verificação: segure o **A** por cerca de 3 segundos e ela instala a última release mesmo que seja mais antiga que a sua. Use para voltar a uma release estável ou reparar uma instalação quebrada, e lembre que não há como desfazer. Prefira uma instalação completa pelo computador se estiver em dúvida.

## Bom saber
- **Primeira vez:** pacotes instalados antes de o atualizador existir não têm a entrada *Update Karman*. Faça uma instalação completa pelo computador primeiro ([como fazer](how-to.md)).
- **Mudanças no menu de boot:** como o `hekate_ipl.ini` é mantido, novas entradas de boot de uma release não chegam até você. Extraia o zip completo ou copie as entradas à mão.
- **Por que reiniciar:** os arquivos do Atmosphere e do Hekate só valem no boot; até lá você está usando os antigos.

## Firmware
O Karman não inclui firmware nem tem uma fonte de firmware. Se você definir `firmware_url` (abaixo), o pacote ganha a entrada **Download firmware (then open Daybreak)**: ela baixa o seu zip para `/firmware/` e depois você abre o **Daybreak** (`switch/daybreak.nro`) e instala. Caso contrário, copie você mesmo os arquivos de firmware para `/firmware/`. Limpe o `/firmware/` antes para não misturar versões, e confirme que o zip traz os arquivos de firmware na raiz dele, não dentro de uma pasta. Use apenas arquivos em que você confia: o Karman não garante a URL.

## Publicando uma release (para quem mantém o projeto)
1. Gere: `GITHUB_TOKEN=$(gh auth token) python3 build.py --version 1.2.0 --build 26101401` → `dist/karman-1.2.0.zip`, `dist/karman-update.zip` e `dist/karman-latest.ini`. O número de build tem 8 dígitos, `YYMMDDNN` (padrão: hoje mais `01`). Vai publicar duas vezes no mesmo dia? Aumente o `NN` (`26101402`). **Nunca reutilize nem diminua um número de build**: os consoles o comparam para decidir o que é mais novo.
2. Publique os três arquivos (os nomes dos assets **precisam** continuar `karman-update.zip` e `karman-latest.ini`):
   ```sh
   gh release create v1.2.0 dist/karman-1.2.0.zip dist/karman-update.zip dist/karman-latest.ini --title "Karman 1.2.0" --notes "O que mudou"
   ```
3. Os consoles que rodarem **Update Karman** passam a receber esta release.

As configurações ficam na tabela `[release]` do `manifest.toml`: `repo` (`dono/nome` no GitHub) e `firmware_url` opcional. Sem `repo`, o build omite a entrada de atualização.
