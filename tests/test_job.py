from datetime import date
from pathlib import Path

from bling_print.config import Config
from bling_print.job import run
from bling_print.state import State


class FakeClient:
    def __init__(self, nfe_situacao=5):
        self.nfe_situacao = nfe_situacao

    def list_orders(self, *a):
        return [{"id": 1}, {"id": 2}]

    def get_order(self, oid):
        return {"id": oid, "numero": str(oid), "notaFiscal": {"id": 10 + oid} if oid == 1 else {},
                "itens": [{"codigo": "A", "descricao": "Item A", "quantidade": 2}], "contato": {"nome": "Cli"}}

    def get_nfe(self, nid):
        return {"situacao": self.nfe_situacao, "linkPdf": "http://x/danfe.pdf"}

    def download(self, url):
        return b"%PDF"

    def get_label(self, oid, fmt):
        return b"^XA^XZ"


def cfg(tmp, **kw):
    base = dict(client_id="", client_secret="", loja_id="", situacoes_ids=[], auto_emit_nfe=False,
                label_printer="", a4_printer="", label_format="ZPL", data_dir=Path(tmp), dry_run=False)
    base.update(kw)
    return Config(**base)


def test_only_orders_with_authorized_nfe_are_printed_and_not_repeated(tmp_path):
    st = State(tmp_path / "s.db")
    r = run(cfg(tmp_path), FakeClient(), st, today=date(2026, 1, 5))
    assert r["printed"] == [1]
    assert r["skipped"][0][0] == 2  # sem NF-e e AUTO_EMIT_NFE=false
    assert (tmp_path / "out/2026-01-05/lista_separacao.pdf").exists()
    r2 = run(cfg(tmp_path), FakeClient(), st, today=date(2026, 1, 5))
    assert r2["printed"] == []  # nao reimprime


def test_unauthorized_nfe_is_skipped(tmp_path):
    r = run(cfg(tmp_path), FakeClient(nfe_situacao=3), State(tmp_path / "s.db"), today=date(2026, 1, 5))
    assert r["printed"] == []
