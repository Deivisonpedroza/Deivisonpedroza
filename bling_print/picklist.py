"""Lista de separacao do dia (A4): soma itens de todos os pedidos e lista cada pedido."""
from collections import defaultdict
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def build(orders: list[dict], path: Path, title: str) -> Path:
    totals: dict[str, list] = defaultdict(lambda: ["", 0.0])
    for o in orders:
        for it in o.get("itens", []):
            key = str(it.get("codigo") or it.get("descricao"))
            totals[key][0] = it.get("descricao", "")
            totals[key][1] += float(it.get("quantidade", 0))

    c = canvas.Canvas(str(path), pagesize=A4)
    w, h = A4
    y = h - 40

    def line(text, size=10, dy=14):
        nonlocal y
        if y < 40:
            c.showPage()
            y = h - 40
        c.setFont("Helvetica", size)
        c.drawString(40, y, text[:105])
        y -= dy

    line(title, 14, 22)
    line(f"{len(orders)} pedidos", 10, 20)
    line("TOTAL A SEPARAR", 12, 18)
    for code, (desc, qty) in sorted(totals.items()):
        line(f"{qty:g} x  {code}  {desc}")
    y -= 10
    line("PEDIDOS", 12, 18)
    for o in orders:
        line(f"#{o.get('numeroLoja') or o.get('numero')}  {o.get('contato', {}).get('nome', '')}", 10)
        for it in o.get("itens", []):
            line(f"    {float(it.get('quantidade', 0)):g} x {it.get('codigo', '')} {it.get('descricao', '')}", 9, 12)
    c.save()
    return Path(path)
