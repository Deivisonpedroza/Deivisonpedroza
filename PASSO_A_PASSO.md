# PASSO A PASSO — Impressão automática de Coruripe

Faça **uma fase por vez, na ordem**. Só passe para a próxima quando a anterior terminar certinho.
Se travar em qualquer ponto, **tire uma foto ou print da tela e me mande**. Não precisa entender nada técnico.

> **REGRA DE OURO:** senhas, tokens, `client_secret` e logins **nunca** são enviados no chat, nem por foto.
> Você mesmo digita ou cola esses dados só dentro dos arquivos do computador da fábrica.
> Eu nunca preciso da sua senha do Bling ou da Shopee.

## Quem faz o quê
| Quem | O que faz |
|---|---|
| **Você (dono)** | Telegram, app do Bling (precisa da senha da conta matriz), comprar equipamento |
| **Quem estiver no computador** | Instalar programas e dar dois cliques nos atalhos numerados |
| **Eu** | Preencher os dados finais, corrigir erros a partir dos prints, ajustar o programa |

---

## FASE 0 — Comprar / conferir (faça já)
- [ ] **Mini-PC com Windows** (liga na tomada e fica ligado o dia todo).
- [ ] **Nobreak** pequeno (liga o mini-PC e a impressora nele). Protege contra queda de energia.
- [ ] **Cabo de rede** (internet por cabo, não por Wi-Fi).
- [ ] **Rolos de etiqueta 100 x 150 mm** (térmica).
- [ ] **A impressora serve?** Olhe a parte de trás dela: tem uma **entrada USB** (encaixe retangular)?
  - **Tem USB** → provavelmente serve. Confira também se o site do fabricante tem **driver para Windows**.
  - **Não tem USB (só Bluetooth/Wi-Fi do celular)** → **não serve** para o robô. Compre uma impressora térmica
    **4x6 polegadas (10x15 cm)**, **USB**, **com driver Windows**. Pergunte ao vendedor: *"Funciona com a etiqueta
    da Shopee 10x15 e tem driver para Windows?"* Marcas comuns: Elgin, Zebra, Argox, Xprinter.
  - Me mande **foto da impressora e da etiqueta embaixo dela** (com o modelo) e eu confirmo antes de você comprar.

---

## FASE 1 — Criar o aviso no Telegram (5 min, no seu celular)
Isso faz o celular apitar quando algo der problema.

1. Abra o **Telegram** (instale se não tiver e crie sua conta).
2. Na lupa, procure por **BotFather** (tem um selo azul de verificado) e toque nele. Toque em **Iniciar**.
3. Envie a mensagem: `/newbot`
4. Ele pergunta o **nome** do bot. Responda: `Impressao Coruripe`
5. Ele pergunta o **usuário** do bot. Tem que terminar com `bot`. Exemplo: `coruripe_impressao_bot`
   (se disser que já existe, troque, por exemplo `coruripe_impressao_2026_bot`).
6. O BotFather responde com um **token**: um código longo parecido com `123456789:AAH...`.
   **Copie e guarde.** É uma senha: não envie para ninguém.
7. Procure pelo **seu bot** (o usuário do passo 5), toque em **Iniciar** e escreva `oi`.

✅ Pronto quando: você tem o token guardado e mandou "oi" para o seu bot.

---

## FASE 2 — Criar o aplicativo no Bling (você, conta MATRIZ)
Isso dá ao robô uma "chave" própria para ler os pedidos. **Não é o seu login.**

> Os nomes dos menus do Bling mudam de vez em quando. Se não achar algum, me mande print que eu indico.

1. No computador, entre em **developer.bling.com.br** e faça login com a **conta da MATRIZ**
   (CNPJ 45.410.144/0001-54).
2. Procure a opção de **criar aplicativo** (algo como *Meus aplicativos → Novo aplicativo*).
3. Preencha:
   - **Nome:** `Robo Impressao Coruripe`
   - **Link de redirecionamento:** `https://localhost`
   - **Permissões:** marque **Pedidos de Vendas**, **Notas Fiscais** e **Logística**
     (marque só consulta/leitura; só marque escrita se o Bling exigir).
4. Salve. O Bling mostra o **client_id** e o **client_secret**.
   **Copie os dois para um bloco de notas.** São senhas: não envie no chat.

✅ Pronto quando: você tem client_id e client_secret anotados.

---

## FASE 3 — Preparar o computador da fábrica
Faça tudo **no mini-PC**.

1. **Instalar o Python:** entre em **python.org/downloads**, baixe e instale.
   ⚠️ Na primeira tela do instalador, **marque a caixinha "Add Python to PATH"** antes de clicar em *Install*.
2. **Instalar o driver da impressora** (site do fabricante). Ligue a impressora por USB e coloque as etiquetas.
   Abra *Configurações → Bluetooth e dispositivos → Impressoras e scanners*: ela deve aparecer na lista.
   Em *Preferências de impressão*, escolha o papel **100 x 150 mm** (ou 4x6 pol).
   **Anote o nome exato** como aparece na lista (ex.: `Label`).
3. **Baixar o SumatraPDF** (programa que manda a impressão): site **sumatrapdfreader.org** →
   baixe a versão **Portable** (um arquivo `SumatraPDF.exe`). Guarde para o passo 5.
4. **Baixar o programa do robô:** no navegador, entre no GitHub, na conta que você usa, no repositório
   **Deivisonpedroza/Deivisonpedroza**. Troque a ramificação (botão escrito `main` ou `master`) para
   **`claude/shopee-orders-daily-notes-print-elvo2y`**. Clique em **Code → Download ZIP**.
5. Extraia o ZIP e **renomeie a pasta para `bling-print`**, deixando em `C:\bling-print`.
   Copie o arquivo **`SumatraPDF.exe`** para dentro dessa pasta.
6. Dê **dois cliques em `1-PREPARAR.bat`** (dentro da pasta). Ele instala o resto sozinho (leva alguns minutos).
   No fim ele abre **dois arquivos no Bloco de Notas** (`.env` e `stores.json`). Vá para a Fase 4.

✅ Pronto quando: o `1-PREPARAR.bat` terminou sem a palavra "erro" em vermelho e abriu os dois arquivos.

---

## FASE 4 — Preencher os dois arquivos
### Arquivo `.env`
Procure as duas linhas abaixo e cole o que você guardou **logo depois do `=`**, sem espaços e sem aspas:
```
TELEGRAM_BOT_TOKEN=cole_aqui_o_token_do_telegram
TELEGRAM_CHAT_ID=
```
Deixe `AUTO_EMIT_NFE=false` **como está** (o Bling já emite as notas; o robô não deve emitir).
Salve (**Ctrl+S**) e feche. O `TELEGRAM_CHAT_ID` você preenche na Fase 5.

### Arquivo `stores.json`
Apague **todo** o conteúdo e cole este texto, trocando só o que está entre `<` `>`:
```
{
  "stores": [
    {
      "name": "coruripe",
      "client_id": "<client_id do Bling>",
      "client_secret": "<client_secret do Bling>",
      "loja_id": "",
      "situacoes_ids": [],
      "label_printer": "<nome exato da impressora no Windows>",
      "print_danfe": false,
      "label_format": "PDF",
      "print_backend": "sumatra"
    }
  ]
}
```
⚠️ Mantenha as **aspas** e as **vírgulas** exatamente como estão. `loja_id` e `situacoes_ids` ficam vazios por
enquanto: eu preencho depois, na Fase 6. Salve (**Ctrl+S**) e feche.

---

## FASE 5 — Testes (só dois cliques, na ordem)
Cada atalho abre uma janela preta. Leia a mensagem final e aperte uma tecla para fechar.

1. **`2-TESTAR-TELEGRAM.bat`**
   - Se aparecer `TELEGRAM_CHAT_ID=123456789`: copie esse número para a linha `TELEGRAM_CHAT_ID=` do `.env`, salve e rode de novo.
   - ✅ **Deve chegar uma mensagem no seu celular.** Se não chegar, me mande print da janela preta.
2. **`3-AUTORIZAR-BLING.bat`** (você precisa estar logado no Bling da matriz)
   - Ele mostra um **link**: copie, cole no navegador e clique em **autorizar**.
   - A página seguinte pode mostrar **erro**: é normal. Olhe o **endereço no topo** do navegador: ele terá algo como `...?code=ABC123&state=...`.
   - Copie só o que vem **depois de `code=`** (até o `&`) e cole na janela preta. Aperte Enter. **Você tem cerca de 1 minuto.**
   - ✅ Deve aparecer `Tokens salvos`. Se der erro, repita (o código expira rápido).
3. **`4-TESTAR-CONEXAO-BLING.bat`** → ✅ deve aparecer `Conexao OK`.
4. **`5-TESTAR-IMPRESSORA.bat`** → ✅ deve **sair uma etiqueta de teste** 10x15 com uma borda e o texto "TESTE 10x15".
   Confira se a borda está inteira e nada foi cortado. Se cortou, ajuste o tamanho do papel nas preferências da impressora.
   **Me mande uma foto da etiqueta de teste.**

---

## FASE 6 — Eu descubro como o Bling responde (só leitura, não altera nada)
1. Dê dois cliques em **`6-LER-BLING-SEM-ALTERAR.bat`**.
2. Ele cria o arquivo **`data\probe.json`**. Esse arquivo mostra só a **estrutura** das respostas do Bling
   (não mostra nome, endereço ou CPF dos clientes).
3. **Abra o arquivo no Bloco de Notas e cole o texto aqui no chat** (ou me mande foto da tela).
4. Eu respondo com **duas linhas** para você colar no `stores.json` (`loja_id` e `situacoes_ids`) e confirmo o que
   mais precisar ajustar.

---

## FASE 7 — Simular e ligar
1. **`7-SIMULAR-SEM-IMPRIMIR.bat`**: roda como se fosse de verdade, **mas não imprime nada**. Ele gera as etiquetas em
   `data\out`. Me diga o que a janela mostrou.
2. **Primeira semana (pedidos reais, com a secretária conferindo junto):** dê dois cliques em **`8-LIGAR-ROBO.bat`**
   e **deixe a janela aberta** (pode minimizar). O robô:
   - olha o Bling a cada 5 minutos;
   - espera **30 minutos** depois de ver o pedido;
   - confere que o pedido **não foi cancelado** e que a nota está **autorizada**;
   - **imprime a etiqueta** da Shopee;
   - **avisa no Telegram** se algo falhar.
   - Na **primeira vez** que ele rodar, os pedidos que já existem são **ignorados de propósito** (e você recebe um aviso).
     Só os pedidos **novos** serão impressos.
3. Para ele ligar **sozinho** quando o computador ligar: dê dois cliques em
   `deploy\windows\instalar-inicio-automatico.bat`, ative o **login automático** do Windows e, na BIOS do mini-PC,
   a opção **"ligar após queda de energia"** (me peça ajuda se não achar).

---

## O que fazer quando chegar um alerta no Telegram
| Alerta | O que significa | O que fazer |
|---|---|---|
| "ainda sem NF-e no Bling após 60 min" | A nota não apareceu (SEFAZ fora do ar?) | Veja o pedido no Bling. O robô continua esperando e imprime quando a nota autorizar. |
| "NF-e não autorizada após 30 min" | A nota ficou pendente/rejeitada | Abra a nota no Bling e veja o motivo. |
| "a etiqueta NÃO saiu" | Nota ok, mas a etiqueta falhou | Confira no Bling *Notas fiscais → Enviar dados para a loja virtual* e se a impressora está ligada com etiquetas. |
| "Robô com erro nesta passada" | Algo travou | Me mande o texto do alerta. |

**Se o robô falhar, o processo manual antigo continua funcionando como reserva.**

## Se algo der errado
| Problema | Solução |
|---|---|
| "Python não encontrado" | Reinstale o Python marcando **Add Python to PATH**. |
| Etiqueta de teste sai cortada | Papel 100x150 mm nas preferências da impressora. |
| Não imprime nada | A impressora aparece em *Impressoras e scanners*? O nome em `label_printer` é idêntico? |
| Erro de autorização do Bling | Refaça `3-AUTORIZAR-BLING.bat` (o código vale ~1 min). |
| Qualquer outra coisa | **Print da janela preta + me mandar.** |
