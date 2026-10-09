import subprocess
from pathlib import Path


def send(printer: str, path: Path, *, raw: bool = False, title: str = "") -> None:
    """Envia um arquivo para uma fila CUPS. raw=True para ZPL direto na termica."""
    cmd = ["lp", "-d", printer]
    if title:
        cmd += ["-t", title]
    if raw:
        cmd += ["-o", "raw"]
    cmd.append(str(path))
    subprocess.run(cmd, check=True, capture_output=True, text=True)
