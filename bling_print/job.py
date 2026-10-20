import logging
import time
from pathlib import Path

from . import printing
from .client import BlingClient
from .config import Settings, Store
from .notify import Notifier
from .state import State

log = logging.getLogger("bling_print")
NFE_AUTORIZADA = 5  # situacao "Autorizada" no Bling (conferir na homologacao)
MAX_PRINT_TRIES = 3
LOOKBACK_DAYS = 3


def tick(cfg: Settings, store: Store, client: BlingClient, state: State, notify: Notifier,
         now: float | None = None) -> None:
    """Uma passada para uma loja. Chamada a cada POLL_SECONDS."""
    now = now or time.time()
    _discover(cfg, store, client, state, notify, now)
    for row in state.with_status(store.name, "waiting"):
        if now - row["first_seen"] >= cfg.delay_minutes * 60:
            _emit(cfg, store, client, state, notify, row, now)
    for row in state.with_status(store.name, "awaiting_nfe"):
        _print_when_authorized(cfg, store, client, state, notify, row, now)


def _discover(cfg, store, client, state, notify, now):
    since = time.strftime("%Y-%m-%d", time.localtime(now - LOOKBACK_DAYS * 86400))
    orders = client.list_orders(store.loja_id, store.situacoes_ids, since)
    first_run = not state.baselined(store.name)
    for o in orders:
        if state.get(store.name, o["id"]) is None:
            # Na 1a execucao, pedidos ja existentes sao ignorados: evita emitir lote antigo por engano.
            state.put(store.name, o["id"], status="baseline" if first_run else "waiting",
                      numero=str(o.get("numero", "")), first_seen=now)
    if first_run:
        state.set_baselined(store.name)
    if first_run and orders:
        notify.alert(f"[{store.name}] Primeira execucao: {len(orders)} pedidos ja existentes foram IGNORADOS "
                     "(nao serao emitidos nem impressos). So pedidos novos entram no fluxo.")


def _emit(cfg, store, client, state, notify, row, now):
    oid = row["order_id"]
    try:
        order = client.get_order(oid)
        situ = str((order.get("situacao") or {}).get("id", ""))
        if store.situacoes_ids and situ not in store.situacoes_ids:
            state.put(store.name, oid, status="changed")  # cancelado ou mudou de situacao durante a espera
            return
        nfe_id = (order.get("notaFiscal") or {}).get("id")
        if nfe_id:
            state.put(store.name, oid, status="awaiting_nfe", nfe_id=str(nfe_id),
                      nfe_requested_at=row["nfe_requested_at"] or now)
            return
        if not cfg.auto_emit_nfe:
            state.put(store.name, oid, status="needs_nfe")
            notify.alert(f"[{store.name}] Pedido {row['numero']} sem NF-e e emissao automatica desligada.")
            return
        if cfg.dry_run:
            log.info("[dry-run] emitiria NF-e do pedido %s", oid)
            return
        # Grava ANTES de emitir: se o processo cair no meio, nunca emitimos duas vezes sozinhos.
        state.put(store.name, oid, status="emitting", nfe_requested_at=now)
        nfe_id = client.generate_nfe(oid)
        state.put(store.name, oid, nfe_id=str(nfe_id))
        client.send_nfe(nfe_id)
        state.put(store.name, oid, status="awaiting_nfe")
    except Exception as e:
        log.exception("Emissao do pedido %s falhou", oid)
        state.put(store.name, oid, status="error", error=str(e)[:300])
        notify.alert(f"[{store.name}] Pedido {row['numero']}: erro ao emitir NF-e. Confira no Bling "
                     f"antes de tentar de novo (o robo NAO tenta de novo sozinho). Erro: {e}")


def _print_when_authorized(cfg, store, client, state, notify, row, now):
    oid = row["order_id"]
    try:
        nfe = client.get_nfe(row["nfe_id"])
        if int(nfe.get("situacao", 0)) != NFE_AUTORIZADA:
            if row["nfe_requested_at"] and now - row["nfe_requested_at"] > cfg.nfe_timeout_minutes * 60 \
                    and row["tries"] == 0:
                state.put(store.name, oid, tries=-1)  # -1 = ja alertado
                notify.alert(f"[{store.name}] Pedido {row['numero']}: NF-e nao autorizada apos "
                             f"{cfg.nfe_timeout_minutes} min (situacao {nfe.get('situacao')}). Ver no Bling.")
            return
        out = cfg.data_dir / "out" / time.strftime("%Y-%m-%d", time.localtime(now))
        out.mkdir(parents=True, exist_ok=True)
        ext = "zpl" if store.label_format == "ZPL" else "pdf"
        label = out / f"{store.name}_{oid}_etiqueta.{ext}"
        label.write_bytes(client.get_label(oid, store.label_format))
        danfe = None
        link = nfe.get("linkPdf") or nfe.get("linkDanfe")
        if store.print_danfe and link:
            danfe = out / f"{store.name}_{oid}_danfe.pdf"
            danfe.write_bytes(client.download(link))
        if cfg.dry_run:
            log.info("[dry-run] imprimiria pedido %s", oid)
            return
        if store.label_printer:
            printing.send(store.label_printer, label, raw=store.label_format == "ZPL", title=f"Etiqueta {oid}")
        if danfe:
            printing.send(store.a4_printer or store.label_printer, danfe, title=f"DANFE {oid}")
        state.put(store.name, oid, status="printed", printed_at=now)
    except Exception as e:
        tries = max(row["tries"], 0) + 1
        log.exception("Impressao do pedido %s falhou (tentativa %d)", oid, tries)
        if tries >= MAX_PRINT_TRIES:
            state.put(store.name, oid, status="error", tries=tries, error=str(e)[:300])
            notify.alert(f"[{store.name}] Pedido {row['numero']}: NF-e autorizada mas NAO imprimiu "
                         f"({tries} tentativas). Erro: {e}")
        else:
            state.put(store.name, oid, tries=tries)
