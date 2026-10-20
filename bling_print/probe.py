"""Leitura SOMENTE de consulta (GET) para descobrir o formato real das respostas do Bling.

Nao emite nada, nao imprime, nao altera nenhum dado. A saida mostra so a ESTRUTURA (nomes dos campos e tipos);
valores de clientes (nome, endereco, CPF etc.) sao mascarados. Pode ser enviada para analise.
"""
import json

from .client import BlingClient, Endpoints

KEEP_VALUES = {"situacao"}  # valores desses campos nao sao dados pessoais e ajudam a mapear os codigos


def shape(obj, key=None, keep=False):
    keep = keep or key in KEEP_VALUES
    if isinstance(obj, dict):
        return {k: shape(v, k, keep) for k, v in obj.items()}
    if isinstance(obj, list):
        return [shape(obj[0], key, keep)] if obj else []
    if keep:
        return obj
    return f"<{type(obj).__name__}>"


def run(client: BlingClient, loja_id: str, situacoes: list[str]) -> dict:
    out: dict = {}
    since = "2000-01-01"
    orders = client.list_orders(loja_id, situacoes, since)[:3]
    out["pedidos_lista (3 primeiros)"] = shape(orders)
    if not orders:
        return out
    oid = orders[0]["id"]
    order = client.get_order(oid)
    out["pedido_detalhe"] = shape(order)
    nfe_id = (order.get("notaFiscal") or {}).get("id")
    if nfe_id:
        out["nfe_detalhe"] = shape(client.get_nfe(nfe_id))
    for fmt in ("PDF", "ZPL"):
        try:
            r = client.request("GET", Endpoints.ETIQUETAS, params={"formato": fmt, "idsVendas[]": [oid]}, raw=True)
            out[f"etiqueta_{fmt}"] = {"status": r.status_code, "content-type": r.headers.get("content-type"),
                                      "bytes": len(r.content)}
        except Exception as e:  # o erro em si mostra se o caminho/parametro esta certo
            out[f"etiqueta_{fmt}"] = {"erro": str(e)[:300]}
    return out


def dump(client, loja_id, situacoes) -> str:
    return json.dumps(run(client, loja_id, situacoes), indent=2, ensure_ascii=False)
