import logging
from datetime import date, timedelta
from pathlib import Path

from . import picklist, printing
from .config import Config
from .state import State

log = logging.getLogger("bling_print")
NFE_AUTORIZADA = 5  # situacao "Autorizada" da NF-e no Bling (conferir na homologacao)


def run(cfg: Config, client, state: State, today: date | None = None, lookback_days: int = 7) -> dict:
    today = today or date.today()
    out_dir = cfg.data_dir / "out" / today.isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)

    since = (today - timedelta(days=lookback_days)).isoformat()
    candidates = client.list_orders(cfg.loja_id, cfg.situacoes_ids, since)
    pending = [o for o in candidates if not state.is_printed(o["id"])]
    log.info("%d pedidos candidatos, %d ainda nao impressos", len(candidates), len(pending))

    done, skipped = [], []
    for summary in pending:
        oid = summary["id"]
        try:
            order = client.get_order(oid)
            nfe_id = (order.get("notaFiscal") or {}).get("id")

            if not nfe_id:
                if not cfg.auto_emit_nfe:
                    skipped.append((oid, "sem NF-e (AUTO_EMIT_NFE=false)"))
                    continue
                if not cfg.dry_run:
                    nfe_id = client.generate_nfe(oid)
                    client.send_nfe(nfe_id)

            nfe = client.get_nfe(nfe_id) if nfe_id else {}
            if nfe_id and int(nfe.get("situacao", 0)) != NFE_AUTORIZADA:
                skipped.append((oid, f"NF-e ainda nao autorizada (situacao {nfe.get('situacao')})"))
                continue

            ext = "zpl" if cfg.label_format == "ZPL" else "pdf"
            label_path = out_dir / f"{oid}_etiqueta.{ext}"
            label_path.write_bytes(client.get_label(oid, cfg.label_format))
            danfe_path = None
            link = nfe.get("linkPdf") or nfe.get("linkDanfe")
            if link:
                danfe_path = out_dir / f"{oid}_danfe.pdf"
                danfe_path.write_bytes(client.download(link))

            order["_label"], order["_danfe"] = label_path, danfe_path
            done.append(order)
        except Exception as e:  # um pedido com problema nao derruba o lote
            log.exception("Pedido %s falhou", oid)
            skipped.append((oid, f"erro: {e}"))

    if done:
        pick = picklist.build(done, out_dir / "lista_separacao.pdf", f"Separacao Shopee {today:%d/%m/%Y}")
        if not cfg.dry_run:
            _print_all(cfg, done, pick)
            for o in done:
                state.mark(o["id"], o.get("numero", ""))

    for oid, why in skipped:
        log.warning("Pedido %s nao impresso: %s", oid, why)
    return {"printed": [o["id"] for o in done], "skipped": skipped}


def _print_all(cfg: Config, orders: list[dict], pick: Path) -> None:
    if cfg.a4_printer:
        printing.send(cfg.a4_printer, pick, title="Lista de separacao")
    for o in orders:
        if cfg.label_printer:
            printing.send(cfg.label_printer, o["_label"], raw=cfg.label_format == "ZPL", title=f"Etiqueta {o['id']}")
        if cfg.a4_printer and o["_danfe"]:
            printing.send(cfg.a4_printer, o["_danfe"], title=f"DANFE {o['id']}")
