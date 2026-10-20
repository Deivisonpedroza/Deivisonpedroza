"""Maquina de estados por pedido. Persistida em SQLite para sobreviver a queda de energia.

Status: waiting -> emitting -> awaiting_nfe -> printed
Terminais/manual: baseline, changed, needs_nfe, error
"""
import sqlite3
from pathlib import Path

COLS = ("status", "numero", "first_seen", "nfe_id", "nfe_requested_at", "printed_at", "tries", "error")


class State:
    def __init__(self, path: Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS orders (
                 store TEXT, order_id TEXT, status TEXT, numero TEXT, first_seen REAL,
                 nfe_id TEXT, nfe_requested_at REAL, printed_at REAL,
                 tries INTEGER DEFAULT 0, error TEXT,
                 PRIMARY KEY (store, order_id))"""
        )
        self.db.execute("CREATE TABLE IF NOT EXISTS baseline (store TEXT PRIMARY KEY)")

    def get(self, store, oid):
        r = self.db.execute("SELECT * FROM orders WHERE store=? AND order_id=?", (store, str(oid))).fetchone()
        return dict(r) if r else None

    def put(self, store, oid, **fields):
        assert set(fields) <= set(COLS), fields
        if self.get(store, oid) is None:
            self.db.execute("INSERT INTO orders (store, order_id) VALUES (?,?)", (store, str(oid)))
        if fields:
            sets = ", ".join(f"{k}=?" for k in fields)
            self.db.execute(
                f"UPDATE orders SET {sets} WHERE store=? AND order_id=?", (*fields.values(), store, str(oid))
            )
        self.db.commit()

    def with_status(self, store, *statuses):
        q = ",".join("?" * len(statuses))
        rows = self.db.execute(f"SELECT * FROM orders WHERE store=? AND status IN ({q})", (store, *statuses))
        return [dict(r) for r in rows]

    def baselined(self, store) -> bool:
        return self.db.execute("SELECT 1 FROM baseline WHERE store=?", (store,)).fetchone() is not None

    def set_baselined(self, store) -> None:
        self.db.execute("INSERT OR IGNORE INTO baseline VALUES (?)", (store,))
        self.db.commit()
