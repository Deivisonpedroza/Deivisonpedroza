import subprocess
from pathlib import Path


def send(printer: str, path: Path, *, raw: bool = False, title: str = "",
         backend: str = "cups", sumatra: str = "SumatraPDF.exe") -> None:
    """Envia arquivo para impressao.

    cups    -> Linux/Raspberry (lp). raw=True manda ZPL direto.
    sumatra -> Windows com o driver do fabricante: imprime PDF em silencio pela fila do Windows.
    """
    if backend == "sumatra":
        if raw:
            raise ValueError("Backend Windows imprime PDF; use label_format=PDF")
        cmd = [sumatra, "-print-to", printer, "-print-settings", "fit", "-silent", str(path)]
    elif backend == "cups":
        cmd = ["lp", "-d", printer]
        if title:
            cmd += ["-t", title]
        if raw:
            cmd += ["-o", "raw"]
        cmd.append(str(path))
    else:
        raise ValueError(f"backend desconhecido: {backend}")
    subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=60)
