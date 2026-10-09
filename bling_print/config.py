import os
from dataclasses import dataclass
from pathlib import Path


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "sim")


@dataclass(frozen=True)
class Config:
    client_id: str
    client_secret: str
    loja_id: str
    situacoes_ids: list[str]
    auto_emit_nfe: bool
    label_printer: str
    a4_printer: str
    label_format: str
    data_dir: Path
    dry_run: bool

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            client_id=os.getenv("BLING_CLIENT_ID", ""),
            client_secret=os.getenv("BLING_CLIENT_SECRET", ""),
            loja_id=os.getenv("BLING_LOJA_ID_SHOPEE", ""),
            situacoes_ids=[s.strip() for s in os.getenv("BLING_SITUACOES_IDS", "").split(",") if s.strip()],
            auto_emit_nfe=_bool("AUTO_EMIT_NFE", False),
            label_printer=os.getenv("LABEL_PRINTER", ""),
            a4_printer=os.getenv("A4_PRINTER", ""),
            label_format=os.getenv("LABEL_FORMAT", "ZPL").upper(),
            data_dir=Path(os.getenv("DATA_DIR", "./data")),
            dry_run=_bool("DRY_RUN", False),
        )
