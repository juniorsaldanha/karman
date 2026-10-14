# Como instalar o Karman

## O que você precisa
- Um Switch que entre em **RCM** (Erista não patcheado, ou Mariko com modchip). Consoles patcheados não servem para este método.
- Uma forma de injetar payload no RCM (um dongle, ou um jig com cabo USB e um app injetor).
- Um cartão microSD (64 GB ou mais é recomendado; só o emuMMC já usa cerca de 30 GB).
- Um PC ou Mac para extrair o zip.
- O `karman-<versão>.zip` mais recente (gerado com `python3 build.py`, veja o README).

O Karman **não** inclui chaves, firmware, jogos nem sigpatches. Use só os seus.

## Passo a passo
1. **Faça backup do cartão SD** e depois [formate em FAT32](format-sd.md).
2. **Extraia o zip na raiz do cartão SD.** Se pedir, mescle as pastas. A raiz do cartão deve ter `atmosphere/`, `bootloader/`, `switch/`, `config/`, `hbmenu.nro` e `hekate_ctcaer_<versão>.bin`. O erro mais comum é uma pasta extra em volta (como `karman-1.0/atmosphere/…`).
3. Coloque o Switch em RCM e **injete o `hekate_ctcaer_<versão>.bin`** (arquivo na raiz do zip; guarde uma cópia no PC para injetar).
4. O menu do Hekate aparece. **Antes do primeiro boot com CFW, [crie um emuMMC](emummc.md)** (recomendado) e faça backup da NAND do sistema.
5. Escolha **Karman (emuMMC)** (ou **Karman (SysNAND)**, se você sabe o que está fazendo). **Stock SysNAND** inicia sem CFW.
6. O console inicia no Horizon com o Atmosphere rodando.

## Usando
- **Menu de homebrew:** segure **R** ao abrir um jogo (ou abra o Álbum) para iniciar o menu de homebrew; o **Sphaira** é o launcher principal. Abrir o Álbum sem jogo aberto também funciona.
- **Overlays (Ultrahand):** pressione **ZL + ZR + D-Pad para baixo** a qualquer momento. Os overlays incluem FPSLocker, Fizeau, sysmodules, emuiibo e o pacote **Karman** (troca de idioma).
- **Instalar jogos/atualizações que você possui:** Goldleaf ou DBI.
- **Saves:** Checkpoint ou JKSV. **FTP:** sys-ftpd-light (ative pelo overlay de sysmodules do Ultrahand).
- **Atualizar o firmware:** Daybreak (`switch/daybreak.nro`) com arquivos de firmware que você fornece.
- **Ports:** o DevilutionX precisa do `DIABDAT.MPQ` na pasta dele; o Perfect Dark precisa da sua ROM em `switch/perfectdark/data/`; o RetroArch precisa dos cores via *Online Updater → Core Downloader*.

## Atualizando o Karman
No console, sem computador: veja [atualizando](updating.md). Pelo computador: baixe ou gere um zip mais novo e extraia por cima do cartão (sobrescrevendo). Seus saves, emuMMC e jogos não são afetados. Extrair de novo também redefine arquivos que o Karman gerencia (`bootloader/hekate_ipl.ini`, `config.ini` do Ultrahand); coloque seus ajustes em `base/` ([personalizar](customize.md)) e gere de novo.

## Solução de problemas
| Problema | Solução |
|---|---|
| Tela preta ao escolher o Karman | Extração aninhada ou `atmosphere/package3` ausente. Extraia de novo na raiz do cartão. |
| A entrada `emuMMC` mostra erro | O emuMMC ainda não foi criado/ativado: [crie](emummc.md). |
| O Hekate não enxerga o SD | Reencaixe o cartão; reformate em FAT32 ([guia](format-sd.md)). |
| Erro do Atmosphere após atualizar o firmware | Atualize o Karman para uma versão compatível com esse firmware. |
| Nada acontece no RCM | Verifique jig/dongle, cabo, e se o injetor confirma o envio do payload. |
