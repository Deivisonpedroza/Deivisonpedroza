# Guia de instalação — Coruripe (Windows)

> Escrito para ser seguido com calma, na ordem. Não pule o teste da impressora (passo 6).

## 0. Antes de comprar: a impressora
Sua impressora hoje funciona só pelo aplicativo do iPhone. **Isso pode significar que ela é só Bluetooth.**
Olhe se ela tem **entrada USB** (um encaixe retangular na traseira). Se tiver, ela pode servir.
Se for só Bluetooth/Wi-Fi do celular, **não serve para o robô**: compre uma que tenha estes requisitos:

- etiqueta térmica **4x6" (100x150 mm)**, impressão térmica direta (sem tinta);
- **conexão USB**;
- **driver para Windows** na página do fabricante (confirme antes de comprar);
- que apareça no Windows como impressora normal (em "Impressoras e scanners").

Não vou indicar modelo nem preço porque não consegui checar o mercado agora. Pergunte ao vendedor:
"Tem driver Windows e funciona com etiqueta da Shopee 10x15?" Marcas comuns no Brasil: Elgin, Zebra, Argox, Xprinter.

## 1. Lista mínima de compra
Computador (mini-PC com Windows), **nobreak**, cabo de rede, cabo USB da impressora, rolos de etiqueta 100x150 mm.

## 2. Criar o bot do Telegram (alertas no seu celular) — grátis, 5 minutos
1. No Telegram, procure **@BotFather** (tem o selo azul de verificado) e toque em **Iniciar**.
2. Envie `/newbot`.
3. Ele pergunta o **nome** do bot: escreva, por exemplo, `Impressao Coruripe`.
4. Ele pergunta o **usuário**: tem que terminar em `bot`, por exemplo `coruripe_impressao_bot`.
5. Ele responde com um **token** (algo como `123456789:AAH...`). **É uma senha: não compartilhe com ninguém.**
6. Procure o seu bot pelo usuário, toque em **Iniciar** e envie `oi`.
7. Coloque o token no arquivo `.env` (passo 5) e rode `python -m bling_print telegram`: ele mostra o seu `TELEGRAM_CHAT_ID`
   e manda uma mensagem de teste no seu celular.

## 3. Criar o app no Bling (conta matriz)
Entre no Bling com a conta matriz → Central de Extensões / Área do Desenvolvedor (developer.bling.com.br) →
criar aplicativo. Anote o **client_id** e o **client_secret** (também são senhas). Em "Link de redirecionamento",
use o que a tela pedir. **Marque somente as permissões necessárias**: pedidos de venda, NF-e e logística.

## 4. Instalar no computador
1. Instale o **Python 3.11 ou mais novo** (python.org) marcando **"Add Python to PATH"**.
2. Instale o **SumatraPDF** (sumatrapdfreader.org), versão normal ou portátil. Anote o caminho do `SumatraPDF.exe`.
3. Instale o **driver da impressora**, ligue por USB e confira em *Configurações → Impressoras* que ela aparece.
   Em *Preferências de impressão*, defina o papel **100 x 150 mm**. Anote o **nome exato** da impressora.
4. Baixe este projeto (GitHub → Code → Download ZIP) e extraia em `C:\bling-print`.
5. Abra o PowerShell em `C:\bling-print` e rode:
```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
copy stores.example.json stores.json
```

## 5. Preencher os arquivos
**`.env`** (abra no Bloco de Notas): `TELEGRAM_BOT_TOKEN=...` e depois `TELEGRAM_CHAT_ID=...`. Deixe `AUTO_EMIT_NFE=false`.

**`stores.json`**: mantenha só a loja Coruripe. Preencha `client_id`, `client_secret`, e em `label_printer` o
**nome exato** da impressora. Mantenha `"label_format": "PDF"` e `"print_backend": "sumatra"`. Se o
SumatraPDF não estiver no PATH, coloque o caminho completo em `"sumatra_path"`.
Para achar `loja_id` e `situacoes_ids`, veja no Bling (Vendas → Pedidos) a loja Shopee e a situação
"Em aberto/Atendido" usada na rotina de vocês; me envie e eu confirmo.

## 6. Testes — nesta ordem
```
.venv\Scripts\python -m bling_print telegram                  # chega mensagem no celular?
.venv\Scripts\python -m bling_print auth --store coruripe     # autoriza o Bling (cole o code)
.venv\Scripts\python -m bling_print check --store coruripe    # conexão OK?
.venv\Scripts\python -m bling_print testprint --store coruripe   # sai etiqueta de teste 10x15 inteira?
.venv\Scripts\python -m bling_print once --dry-run            # roda sem emitir nem imprimir
```
Só avance quando todos funcionarem. Se a etiqueta de teste sair cortada, ajuste o papel nas preferências da impressora.

## 7. Ligar de verdade (em 2 etapas)
1. **Semana 1 — só imprime:** deixe `AUTO_EMIT_NFE=false`. A secretária continua emitindo; o robô imprime a etiqueta
   das notas já autorizadas. Confira que cada etiqueta sai certa e que nenhuma sai duas vezes.
2. **Depois, emissão automática:** coloque `AUTO_EMIT_NFE=true` **depois** de conferir com um pedido real que a
   nota saiu pelo CNPJ da matriz (45.410.144/0001-54) e com os impostos corretos.

Para o robô rodar sozinho: dê dois cliques em `deploy\windows\instalar-inicio-automatico.bat` e ative o login
automático do Windows. Na BIOS do mini-PC, ative "ligar após queda de energia".
