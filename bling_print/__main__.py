import argparse
import logging
import sys

from .client import BlingClient
from .config import Config
from .job import run
from .state import State


def main() -> int:
    p = argparse.ArgumentParser(prog="bling_print")
    p.add_argument("cmd", choices=["auth", "run", "check"])
    p.add_argument("--dry-run", action="store_true", help="gera arquivos, mas nao imprime nem emite")
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = Config.from_env()
    if args.dry_run:
        object.__setattr__(cfg, "dry_run", True)
    if not (cfg.client_id and cfg.client_secret):
        print("Defina BLING_CLIENT_ID e BLING_CLIENT_SECRET no .env")
        return 2
    client = BlingClient(cfg.client_id, cfg.client_secret, cfg.data_dir / "tokens.json")

    if args.cmd == "auth":
        print("1) Abra o link de autorizacao do seu app no Bling (Central de Extensoes > seu app).")
        print("2) Autorize e copie o parametro 'code' da URL de retorno (vale ~1 minuto).")
        client.exchange_code(input("code: ").strip())
        print("Tokens salvos.")
        return 0

    if args.cmd == "check":
        orders = client.list_orders(cfg.loja_id, cfg.situacoes_ids, "2000-01-01")[:1]
        print("Conexao OK. Exemplo de pedido:", orders[0] if orders else "nenhum encontrado")
        return 0

    result = run(cfg, client, State(cfg.data_dir / "state.db"))
    print(f"Impressos: {len(result['printed'])} | Pulados: {len(result['skipped'])}")
    return 1 if result["skipped"] else 0


if __name__ == "__main__":
    sys.exit(main())
