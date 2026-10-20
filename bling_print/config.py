import json
import os
from dataclasses import dataclass, field
from pathlib import Path


def load_env(path: str = ".env") -> None:
    """Le o arquivo .env (no Windows nao ha EnvironmentFile do systemd). Nao sobrescreve variaveis ja definidas."""
    f = Path(path)
    if not f.exists():
        return
    for line in f.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "sim")


@dataclass(frozen=True)
class Store:
    name: str
    client_id: str
    client_secret: str
    loja_id: str
    situacoes_ids: list[str]
    label_printer: str
    a4_printer: str = ""
    print_danfe: bool = True
    label_format: str = "ZPL"
    print_backend: str = "cups"  # "cups" (Linux) ou "sumatra" (Windows)
    sumatra_path: str = "SumatraPDF.exe"


@dataclass(frozen=True)
class Settings:
    stores: list[Store]
    auto_emit_nfe: bool
    delay_minutes: int
    poll_seconds: int
    nfe_timeout_minutes: int
    data_dir: Path
    dry_run: bool
    telegram_token: str = ""
    telegram_chat_id: str = ""

    def problems(self) -> list[str]:
        """Campos que PRECISAM estar preenchidos antes de rodar o robo de verdade."""
        out = []
        for st in self.stores:
            for field_name, label in (("client_id", "client_id"), ("client_secret", "client_secret"),
                                      ("loja_id", "loja_id"), ("situacoes_ids", "situacoes_ids"),
                                      ("label_printer", "label_printer")):
                if not getattr(st, field_name):
                    out.append(f"[{st.name}] falta preencher {label} no stores.json")
        return out

    @classmethod
    def load(cls, stores_file: str | None = None) -> "Settings":
        load_env()
        path = Path(stores_file or os.getenv("STORES_FILE", "stores.json"))
        raw = json.loads(path.read_text())
        stores = [
            Store(
                name=s["name"],
                client_id=s["client_id"],
                client_secret=s["client_secret"],
                loja_id=str(s.get("loja_id", "")),
                situacoes_ids=[str(x) for x in s.get("situacoes_ids", [])],
                label_printer=s.get("label_printer", ""),
                a4_printer=s.get("a4_printer", ""),
                print_danfe=s.get("print_danfe", True),
                label_format=s.get("label_format", "ZPL").upper(),
                print_backend=s.get("print_backend", "cups"),
                sumatra_path=s.get("sumatra_path", "SumatraPDF.exe"),
            )
            for s in raw["stores"]
        ]
        return cls(
            stores=stores,
            auto_emit_nfe=_bool("AUTO_EMIT_NFE", False),
            delay_minutes=int(os.getenv("DELAY_MINUTES", "30")),
            poll_seconds=int(os.getenv("POLL_SECONDS", "300")),
            nfe_timeout_minutes=int(os.getenv("NFE_TIMEOUT_MINUTES", "30")),
            data_dir=Path(os.getenv("DATA_DIR", "./data")),
            dry_run=_bool("DRY_RUN", False),
            telegram_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
        )
