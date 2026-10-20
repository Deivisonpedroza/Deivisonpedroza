# Robô Shopee → Bling → NF-e → impressora térmica (2 lojas)

Serviço que fica ligado num Raspberry Pi / mini-PC em cada local de impressão.
A cada 5 min ele olha o Bling de cada loja (Coruripe, Holambra). Para cada pedido novo:

1. espera **30 min** (conta a partir de quando o robô viu o pedido), para dar tempo de cancelamento;
2. confere de novo se o pedido continua válido (se foi cancelado, **não emite**);
3. emite a NF-e no Bling (se `AUTO_EMIT_NFE=true`) e espera autorizar;
4. imprime a etiqueta 10x15 na térmica da loja (o DANFE A4 só sai se a loja tiver `a4_printer`);
5. manda **alerta no Telegram** se algo falhar (ninguém precisa ficar olhando tela).

## Proteções contra erro fiscal
- Estado de cada pedido fica em SQLite. O robô grava "emitindo" **antes** de chamar o Bling:
  se cair a energia no meio, ele **nunca** emite de novo sozinho; avisa e espera um humano.
- Se o pedido já tem NF-e no Bling, ela é reaproveitada, nunca duplicada.
- Na 1ª execução de cada loja, pedidos que já existem são **ignorados** (evita emitir lote antigo).
- `AUTO_EMIT_NFE=false` (padrão): só imprime notas que alguém já emitiu. Ligue só após testar.
- Erro ao emitir ou ao imprimir = alerta. Impressão tenta 3x; emissão não tenta de novo.

## Instalação (em cada Pi)
```bash
sudo apt install -y cups python3-venv git
sudo usermod -aG lpadmin $USER      # cadastre a térmica em http://localhost:631 (fila "Raw" se for ZPL)
git clone <este repo> /opt/bling-print && cd /opt/bling-print
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env && cp stores.example.json stores.json && chmod 600 .env stores.json   # preencher
.venv/bin/python -m bling_print auth  --store coruripe     # 1x por loja
.venv/bin/python -m bling_print check --store coruripe
.venv/bin/python -m bling_print once --dry-run              # testa sem emitir/imprimir
sudo cp deploy/bling-print.service /etc/systemd/system/ && sudo systemctl enable --now bling-print
```
Use SSD (não só cartão SD) e, se possível, nobreak: queda de energia corrompe cartão SD.
Se cada loja tem seu Pi, deixe no `stores.json` de cada um apenas a loja daquele local.

## Conferir antes do uso real
Caminhos de endpoint em `bling_print/client.py` (`Endpoints`), o número da situação "autorizada"
(`NFE_AUTORIZADA` em `job.py`) e o formato da etiqueta/DANFE para a térmica foram escritos sem a
referência oficial do Bling. Teste com `--dry-run` e com 1 pedido real antes de ligar `AUTO_EMIT_NFE`.

## Testes
`.venv/bin/python -m pytest`
