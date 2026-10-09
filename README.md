# Impressão diária de pedidos Shopee (via Bling)

Robô que roda num Raspberry Pi / mini-PC na fábrica: busca pedidos Shopee no Bling,
confere a NF-e, baixa etiqueta + DANFE, monta a lista de separação e imprime.
Seg–sex 13:30, sábado 08:00 (ver `deploy/crontab.txt`).

## Segurança fiscal
- `AUTO_EMIT_NFE=false` (padrão): só imprime pedidos cuja NF-e já está **autorizada**. Os demais são
  listados no log como "pulados".
- Ligue `AUTO_EMIT_NFE=true` só depois de uma semana de testes limpa. NF-e autorizada não se apaga.
- Pedido impresso fica registrado em `data/state.db` e nunca é reimpresso.

## Instalação no Pi (Raspberry Pi OS / Debian)
```bash
sudo apt install -y cups python3-venv git
sudo usermod -aG lpadmin $USER
# Adicione a impressora em http://localhost:631 (Administration > Add Printer).
# Termica ZPL: use o driver "Raw Queue". Confira o nome com: lpstat -p
git clone <este repo> /opt/bling-print && cd /opt/bling-print
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env && chmod 600 .env   # preencha
.venv/bin/python -m bling_print auth      # autoriza o app (uma vez)
.venv/bin/python -m bling_print check     # confirma a conexão
.venv/bin/python -m bling_print run --dry-run   # gera arquivos em data/out sem imprimir
crontab deploy/crontab.txt
```
O refresh token do Bling vale ~30 dias; o robô renova a cada execução, então rodar diariamente
mantém a autorização viva. Se o Pi ficar desligado por mais de 30 dias, rode `auth` de novo.

## ATENÇÃO: conferir antes do uso real
Os caminhos de endpoint estão em `bling_print/client.py` (classe `Endpoints`) e foram escritos
sem acesso à referência oficial. Confira em developer.bling.com.br: geração de NF-e a partir do
pedido, envio da NF-e, `situacao` "Autorizada" (constante `NFE_AUTORIZADA` em `job.py`) e o
endpoint/formato de etiquetas. Use `--dry-run` até tudo bater.

## Testes
`.venv/bin/python -m pytest`
