"""Registro de pedidos ja impressos, para nunca imprimir duas vezes."""
import sqlite3
import time
from pathlib import Path


class State:
    def __init__(self, path: Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS printed (order_id TEXT PRIMARY KEY, numero TEXT, ts REAL)"
        )

    def is_printed(self, order_id) -> bool:
        cur = self.db.execute("SELECT 1 FROM printed WHERE order_id=?", (str(order_id),))
        return cur.fetchone() is not None

    def mark(self, order_id, numero="") -> None:
        self.db.execute(
            "INSERT OR REPLACE INTO printed VALUES (?,?,?)", (str(order_id), str(numero), time.time())
        )
        self.db.commit()
