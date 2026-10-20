"""Etiqueta de teste 10x15 cm para validar impressora, driver e tamanho antes de usar pedidos reais."""
from pathlib import Path

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from . import printing
from .config import Store


def run(store: Store, data_dir: Path) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    if store.label_format == "ZPL":
        f = data_dir / "teste.zpl"
        f.write_text("^XA^PW800^LL1200^FO40,40^GB720,1120,4^FS^FO80,120^A0N,60,60^FDTESTE 10x15^FS"
                     f"^FO80,220^A0N,40,40^FD{store.name}^FS^XZ")
    else:
        f = data_dir / "teste.pdf"
        c = canvas.Canvas(str(f), pagesize=(100 * mm, 150 * mm))
        c.rect(4 * mm, 4 * mm, 92 * mm, 142 * mm)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(10 * mm, 120 * mm, "TESTE 10x15")
        c.setFont("Helvetica", 14)
        c.drawString(10 * mm, 108 * mm, f"Loja: {store.name}")
        c.drawString(10 * mm, 14 * mm, "Se as bordas estao visiveis, o tamanho esta certo.")
        c.save()
    printing.send(store.label_printer, f, raw=store.label_format == "ZPL", title="Teste",
                  backend=store.print_backend, sumatra=store.sumatra_path)
    return f
