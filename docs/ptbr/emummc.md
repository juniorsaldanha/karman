# emuMMC (emuNAND)

Um **emuMMC** é uma cópia da NAND do sistema do seu Switch guardada no cartão SD. Você roda o CFW Atmosphere a partir da cópia e deixa a NAND real (SysNAND) limpa. É a forma recomendada de usar o Karman.

O Karman traz duas entradas de boot:
- **Karman (emuMMC)**: usa `emummcforce=1`. Se nenhum emuMMC estiver ativo, ele para com um erro em vez de iniciar a SysNAND sem avisar.
- **Karman (SysNAND)**: CFW na NAND real. Só se você sabe o que está fazendo.

## 1. Faça backup primeiro
No Hekate vá em **Nyx → Tools → Backup eMMC**: faça backup de **eMMC BOOT0 & BOOT1** (contém o PRODINFO, os dados de calibração únicos do seu console) e **eMMC RAW GPP**. Copie o backup do cartão SD para o PC e guarde bem. Um PRODINFO perdido não pode ser recriado.

## 2. Crie o emuMMC
Você precisa de cerca de **30 GB livres** (mais para uma cópia completa). Escolha um tipo.

### Em partição (mais rápido, recomendado para cartões grandes)
Usa uma partição raw dedicada. **Isto reparticiona e apaga o cartão SD**, então faça backup dos arquivos antes.
1. **Nyx → Tools → Partition SD Card**.
2. Arraste o controle para reservar o tamanho do emuMMC (pelo menos ~30 GB) e deixe o restante como partição FAT32.
3. Inicie. Depois restaure seus arquivos (extraia o zip do Karman de novo).
4. **Nyx → emuMMC → Create emuMMC → SD Partition** e siga as instruções. Aguarde a cópia.

### Em arquivos (mais simples, sem reparticionar)
Guarda o emuMMC como arquivos na partição FAT32, em partes de 4 GB.
1. **Nyx → emuMMC → Create emuMMC → SD File**.
2. Siga as instruções para copiar a SysNAND e aguarde terminar.

Depois, **Nyx → emuMMC → Change emuMMC** mostra e seleciona o ativo. Inicie **Karman (emuMMC)**.

## 3. Mantenha offline
Um console com CFW que se conecta aos servidores da Nintendo corre risco de banimento. A proteção usual é bloquear esses hosts no emuMMC com os arquivos hosts do Atmosphere. O zip do Atmosphere não traz um, e o Karman não impõe nenhum. Para bloquear, crie `atmosphere/hosts/emummc.txt` no SD com:

```
# Block Nintendo servers
127.0.0.1 *nintendo.com
127.0.0.1 *nintendo.net
127.0.0.1 *nintendo.jp
127.0.0.1 *nintendo.co.jp
127.0.0.1 *nintendo.co.uk
127.0.0.1 *nintendo-europe.com
127.0.0.1 *nintendowifi.net
127.0.0.1 *nintendoswitch.com
127.0.0.1 *nintendoswitch.com.cn
127.0.0.1 *nintendoswitch.cn
```

Use a SysNAND original (sem CFW) para tudo o que for online. Não copie saves ou contas entre as duas sem entender as consequências.

## 4. Atualizando o firmware dentro do emuMMC
Inicie **Karman (emuMMC)**, abra o **Daybreak** (`switch/daybreak.nro`), aponte para uma pasta com os arquivos de firmware que **você fornece** (o Karman não inclui firmware) e escolha a opção de instalar. Depois de atualizar o firmware, atualize o Karman também (o Atmosphere precisa suportar esse firmware).

## Solução de problemas
| Problema | Solução |
|---|---|
| "emuMMC not found/enabled" | Crie-o (passo 2), ou escolha **Karman (SysNAND)** conscientemente. |
| Falta de espaço | Libere espaço ou use um cartão maior; o em arquivos precisa de ~30 GB livres. |
| Inicia na versão de firmware original | Confira a entrada: **Stock SysNAND** não carrega CFW. |
