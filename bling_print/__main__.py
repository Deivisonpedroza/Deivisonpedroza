import argparse
import logging
import sys
import time

from .client import BlingClient
from .config import Settings
from .job import tick
from .notify import Notifier
from .state import State


def _clients(cfg: Settings) -> dict[str, BlingClient]:
    return {s.name: BlingClient(s.client_id, s.client_secret, cfg.data_dir / f"tokens_{s.name}.json")
            for s in cfg.stores}


def main() -> int:
    p = argparse.ArgumentParser(prog="bling_print")
    p.add_argument("cmd", choices=["auth", "check", "once", "watch"])
    p.add_argument("--store", help="nome da loja (para auth/check)")
    p.add_argument("--dry-run", action="store_true", help="nao emite NF-e nem imprime")
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    cfg = Settings.load()
    if args.dry_run:
        object.__setattr__(cfg, "dry_run", True)
    clients = _clients(cfg)
    state = State(cfg.data_dir / "state.db")
    notify = Notifier(cfg.telegram_token, cfg.telegram_chat_id)

    if args.cmd in ("auth", "check"):
        if not args.store:
            print("Use --store NOME. Lojas:", ", ".join(clients))
            return 2
        c = clients[args.store]
        if args.cmd == "auth":
            print("Autorize o app dessa loja no Bling e cole o 'code' da URL de retorno (vale ~1 min).")
            c.exchange_code(input("code: ").strip())
            print("Tokens salvos.")
        else:
            st = next(s for s in cfg.stores if s.name == args.store)
            found = c.list_orders(st.loja_id, st.situacoes_ids, "2000-01-01")[:1]
            print("Conexao OK. Exemplo:", found[0] if found else "nenhum pedido")
        return 0

    while True:
        for s in cfg.stores:
            try:  # uma loja com problema nao para a outra
                tick(cfg, s, clients[s.name], state, notify)
            except Exception as e:
                logging.exception("Loja %s falhou nesta passada", s.name)
                notify.alert(f"[{s.name}] Robo com erro nesta passada: {e}")
        if args.cmd == "once":
            return 0
        time.sleep(cfg.poll_seconds)


if __name__ == "__main__":
    sys.exit(main())
