from pathlib import Path

import pytest

from bling_print import job, printing
from bling_print.config import Settings, Store
from bling_print.notify import Notifier
from bling_print.state import State

T0 = 1_800_000_000.0
ELIG = "15"


class Notes(Notifier):
    def __init__(self):
        super().__init__()
        self.msgs = []

    def alert(self, text):
        self.msgs.append(text)


class Fake:
    def __init__(self):
        self.orders = []
        self.has_nfe = {}
        self.sit = {}
        self.gen_calls = 0
        self.fail_generate = False
        self.nfe_situacao = 5

    def list_orders(self, *a):
        return [{"id": i, "numero": f"N{i}"} for i in self.orders]

    def get_order(self, oid):
        oid = int(oid)
        nf = {"id": self.has_nfe[oid]} if oid in self.has_nfe else {}
        return {"id": oid, "situacao": {"id": self.sit.get(oid, int(ELIG))}, "notaFiscal": nf}

    def generate_nfe(self, oid):
        oid = int(oid)
        self.gen_calls += 1
        if self.fail_generate:
            raise RuntimeError("SEFAZ fora")
        return 900 + oid

    def send_nfe(self, nid):
        pass

    def get_nfe(self, nid):
        return {"situacao": self.nfe_situacao, "linkPdf": "http://x"}

    def download(self, url):
        return b"%PDF"

    def get_label(self, oid, fmt):
        return b"^XA^XZ"


@pytest.fixture
def env(tmp_path, monkeypatch):
    printed = []
    monkeypatch.setattr(printing, "send", lambda p, f, **k: printed.append((p, Path(f).name)))
    store = Store("coruripe", "id", "sec", "1", [ELIG], "termica")
    cfg = Settings([store], True, 30, 300, 30, tmp_path, False)
    return cfg, store, Fake(), State(tmp_path / "s.db"), Notes(), printed


def run(env, t):
    cfg, store, cl, st, n, _ = env
    job.tick(cfg, store, cl, st, n, now=T0 + t)


def test_first_run_ignores_existing_orders(env):
    env[2].orders = [1, 2]
    run(env, 0)
    run(env, 3600)
    assert env[2].gen_calls == 0 and env[5] == []
    assert "IGNORADOS" in env[4].msgs[0]


def test_waits_30_min_then_emits_and_prints_once(env):
    cl = env[2]
    run(env, 0)  # baseline vazio
    cl.orders = [7]
    run(env, 60)
    run(env, 60 + 29 * 60)
    assert cl.gen_calls == 0  # ainda dentro dos 30 min
    run(env, 60 + 30 * 60)
    assert cl.gen_calls == 1
    run(env, 60 + 31 * 60)
    run(env, 60 + 40 * 60)
    assert cl.gen_calls == 1  # nunca emite duas vezes
    assert [f for _, f in env[5]] == ["coruripe_7_etiqueta.zpl"]  # sem a4_printer: DANFE nao vai p/ termica


def test_cancelled_during_wait_is_not_emitted(env):
    cl = env[2]
    run(env, 0)
    cl.orders = [7]
    run(env, 60)
    cl.sit[7] = 12  # virou cancelado
    run(env, 60 + 31 * 60)
    assert cl.gen_calls == 0 and env[3].get("coruripe", 7)["status"] == "changed"


def test_emission_error_alerts_and_never_retries(env):
    cl = env[2]
    run(env, 0)
    cl.orders = [7]
    cl.fail_generate = True
    run(env, 60)
    run(env, 60 + 31 * 60)
    run(env, 60 + 40 * 60)
    assert cl.gen_calls == 1
    assert env[3].get("coruripe", 7)["status"] == "error" and "SEFAZ" in env[4].msgs[-1]


def test_existing_nfe_is_reused_not_reissued(env):
    cl = env[2]
    run(env, 0)
    cl.orders = [7]
    cl.has_nfe[7] = 555
    run(env, 60)
    run(env, 60 + 31 * 60)
    run(env, 60 + 32 * 60)
    assert cl.gen_calls == 0 and len(env[5]) == 1


def test_unauthorized_nfe_alerts_after_timeout(env):
    cl = env[2]
    cl.nfe_situacao = 3
    run(env, 0)
    cl.orders = [7]
    run(env, 60)
    run(env, 60 + 31 * 60)
    run(env, 60 + 70 * 60)
    assert env[5] == [] and "nao autorizada" in env[4].msgs[-1]


def test_danfe_printed_only_on_a4_printer(env, tmp_path):
    cfg, _, cl, st, n, printed = env
    store = Store("coruripe", "id", "sec", "1", [ELIG], "termica", a4_printer="laser")
    cl.orders = []
    job.tick(cfg, store, cl, st, n, now=T0)
    cl.orders = [7]
    job.tick(cfg, store, cl, st, n, now=T0 + 60)
    job.tick(cfg, store, cl, st, n, now=T0 + 60 + 31 * 60)
    job.tick(cfg, store, cl, st, n, now=T0 + 60 + 32 * 60)
    assert ("termica", "coruripe_7_etiqueta.zpl") in printed and ("laser", "coruripe_7_danfe.pdf") in printed


def test_windows_backend_builds_silent_pdf_command(monkeypatch):
    calls = []
    monkeypatch.setattr(printing.subprocess, "run", lambda cmd, **k: calls.append(cmd))
    printing.send("Label", Path("e.pdf"), backend="sumatra", sumatra="S.exe")
    assert calls[0][:3] == ["S.exe", "-print-to", "Label"] and "-silent" in calls[0]
    with pytest.raises(ValueError):
        printing.send("Label", Path("e.zpl"), raw=True, backend="sumatra")


def test_load_env_reads_file_without_overriding(tmp_path, monkeypatch):
    from bling_print.config import load_env
    f = tmp_path / ".env"
    f.write_text('# c\nAUTO_EMIT_NFE="true"\nPOLL_SECONDS=60\nJA_DEFINIDA=nova\n', encoding="utf-8")
    monkeypatch.setenv("JA_DEFINIDA", "antiga")
    monkeypatch.delenv("AUTO_EMIT_NFE", raising=False)
    load_env(str(f))
    import os
    assert os.environ["AUTO_EMIT_NFE"] == "true" and os.environ["JA_DEFINIDA"] == "antiga"
    monkeypatch.delenv("AUTO_EMIT_NFE")
    monkeypatch.delenv("POLL_SECONDS")


def test_find_chat_id_returns_latest_chat(monkeypatch):
    from bling_print import notify

    class R:
        def raise_for_status(self): pass
        def json(self): return {"result": [{"message": {"chat": {"id": 1, "first_name": "A"}}},
                                           {"message": {"chat": {"id": 42, "first_name": "Deivison"}}}]}
    monkeypatch.setattr(notify.requests, "get", lambda *a, **k: R())
    assert notify.find_chat_id("tok") == ("42", "Deivison")


def test_testprint_pdf_and_zpl(tmp_path, monkeypatch):
    from bling_print import testprint
    sent = []
    monkeypatch.setattr(printing, "send", lambda p, f, **k: sent.append((p, Path(f).suffix, k["raw"])))
    testprint.run(Store("c", "i", "s", "1", [], "Label", label_format="PDF", print_backend="sumatra"), tmp_path)
    testprint.run(Store("c", "i", "s", "1", [], "Label", label_format="ZPL"), tmp_path)
    assert sent == [("Label", ".pdf", False), ("Label", ".zpl", True)]


def test_without_auto_emit_waits_for_bling_nfe_alerts_once_then_prints(env):
    import dataclasses
    cfg, store, cl, st, n, printed = env
    cfg = dataclasses.replace(cfg, auto_emit_nfe=False)
    job.tick(cfg, store, cl, st, n, now=T0)
    cl.orders = [7]
    job.tick(cfg, store, cl, st, n, now=T0 + 60)
    job.tick(cfg, store, cl, st, n, now=T0 + 40 * 60)  # passou a espera, ainda sem NF: nao alerta ainda
    assert cl.gen_calls == 0 and not n.msgs[1:]
    job.tick(cfg, store, cl, st, n, now=T0 + 100 * 60)  # passou 30+30 min
    job.tick(cfg, store, cl, st, n, now=T0 + 110 * 60)
    assert len([m for m in n.msgs if "sem NF-e" in m]) == 1  # alerta uma unica vez
    cl.has_nfe[7] = 555  # o Bling autorizou depois
    job.tick(cfg, store, cl, st, n, now=T0 + 120 * 60)
    job.tick(cfg, store, cl, st, n, now=T0 + 121 * 60)
    assert cl.gen_calls == 0 and [f for _, f in printed] == ["coruripe_7_etiqueta.zpl"]


def test_probe_shape_masks_personal_values_keeps_situacao():
    from bling_print.probe import shape
    r = shape({"contato": {"nome": "Maria", "cpf": "1"}, "situacao": {"id": 9, "valor": 1}, "itens": [{"q": 2}]})
    assert r == {"contato": {"nome": "<str>", "cpf": "<str>"}, "situacao": {"id": 9, "valor": 1},
                 "itens": [{"q": "<int>"}]}
