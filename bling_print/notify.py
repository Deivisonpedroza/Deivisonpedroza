import logging

import requests

log = logging.getLogger("bling_print")


class Notifier:
    """Avisa o dono por Telegram quando algo precisa de acao humana. Sem config, so grava no log."""

    def __init__(self, token: str = "", chat_id: str = ""):
        self.token, self.chat_id = token, chat_id

    def alert(self, text: str) -> None:
        log.error("ALERTA: %s", text)
        if not (self.token and self.chat_id):
            return
        try:
            requests.post(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                json={"chat_id": self.chat_id, "text": text[:3500]},
                timeout=15,
            )
        except requests.RequestException:
            log.exception("Falha ao enviar alerta")
