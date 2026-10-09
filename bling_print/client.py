"""Cliente minimo da API v3 do Bling.

TODOS os caminhos de endpoint ficam na classe Endpoints. Eles foram escritos a partir
da documentacao publica da v3 e DEVEM ser conferidos em developer.bling.com.br antes do
primeiro uso real (rode `python -m bling_print check`).
"""
import base64
import json
import os
import time
from pathlib import Path

import requests

API = "https://api.bling.com.br/Api/v3"
MIN_INTERVAL = 0.4  # limite oficial: 3 req/s por conta; sobra margem


class Endpoints:
    TOKEN = "/oauth/token"
    PEDIDOS = "/pedidos/vendas"
    PEDIDO = "/pedidos/vendas/{id}"
    GERAR_NFE = "/pedidos/vendas/{id}/gerar-nfe"
    NFE = "/nfe/{id}"
    NFE_ENVIAR = "/nfe/{id}/enviar"
    ETIQUETAS = "/logisticas/etiquetas"


class BlingError(RuntimeError):
    pass


class BlingClient:
    def __init__(self, client_id: str, client_secret: str, token_file: Path):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_file = Path(token_file)
        self._last_call = 0.0
        self._tokens: dict = {}
        if self.token_file.exists():
            self._tokens = json.loads(self.token_file.read_text())

    # ---------- OAuth ----------
    def _basic(self) -> str:
        raw = f"{self.client_id}:{self.client_secret}".encode()
        return "Basic " + base64.b64encode(raw).decode()

    def _save(self, tokens: dict) -> None:
        self._tokens = tokens
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.token_file.with_suffix(".tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            json.dump(tokens, f)
        os.replace(tmp, self.token_file)

    def _token_request(self, data: dict) -> None:
        r = requests.post(
            API + Endpoints.TOKEN,
            data=data,
            headers={"Authorization": self._basic(), "enable-jwt": "1"},
            timeout=30,
        )
        if r.status_code != 200:
            raise BlingError(f"Falha no OAuth ({r.status_code}): {r.text[:200]}")
        self._save(r.json())

    def exchange_code(self, code: str) -> None:
        self._token_request({"grant_type": "authorization_code", "code": code})

    def refresh(self) -> None:
        rt = self._tokens.get("refresh_token")
        if not rt:
            raise BlingError("Sem refresh_token. Rode: python -m bling_print auth")
        self._token_request({"grant_type": "refresh_token", "refresh_token": rt})

    # ---------- HTTP ----------
    def _throttle(self) -> None:
        wait = MIN_INTERVAL - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def request(self, method: str, path: str, *, params=None, json_body=None, raw=False):
        if not self._tokens.get("access_token"):
            self.refresh()
        for attempt in range(4):
            self._throttle()
            r = requests.request(
                method,
                API + path,
                params=params,
                json=json_body,
                headers={
                    "Authorization": f"Bearer {self._tokens['access_token']}",
                    "enable-jwt": "1",
                },
                timeout=60,
            )
            if r.status_code == 401 and attempt == 0:
                self.refresh()
                continue
            if r.status_code == 429:
                time.sleep(2 ** (attempt + 1))
                continue
            if r.status_code >= 400:
                raise BlingError(f"{method} {path} -> {r.status_code}: {r.text[:300]}")
            return r if raw else (r.json() if r.content else {})
        raise BlingError(f"{method} {path}: tentativas esgotadas")

    # ---------- Operacoes ----------
    def list_orders(self, loja_id: str, situacoes: list[str], data_inicial: str) -> list[dict]:
        orders, page = [], 1
        while True:
            params = {
                "pagina": page,
                "limite": 100,
                "dataInicial": data_inicial,
                "idsSituacoes[]": situacoes,
            }
            if loja_id:
                params["idLoja"] = loja_id
            data = self.request("GET", Endpoints.PEDIDOS, params=params).get("data", [])
            orders += data
            if len(data) < 100:
                return orders
            page += 1

    def get_order(self, order_id) -> dict:
        return self.request("GET", Endpoints.PEDIDO.format(id=order_id)).get("data", {})

    def generate_nfe(self, order_id) -> int:
        d = self.request("POST", Endpoints.GERAR_NFE.format(id=order_id)).get("data", {})
        return d["id"]

    def send_nfe(self, nfe_id) -> None:
        self.request("POST", Endpoints.NFE_ENVIAR.format(id=nfe_id))

    def get_nfe(self, nfe_id) -> dict:
        return self.request("GET", Endpoints.NFE.format(id=nfe_id)).get("data", {})

    def download(self, url: str) -> bytes:
        self._throttle()
        r = requests.get(url, timeout=60)
        if r.status_code != 200:
            raise BlingError(f"Download falhou ({r.status_code}): {url}")
        return r.content

    def get_label(self, order_id, fmt: str) -> bytes:
        r = self.request(
            "GET",
            Endpoints.ETIQUETAS,
            params={"formato": fmt, "idsVendas[]": [order_id]},
            raw=True,
        )
        if "json" in r.headers.get("content-type", ""):
            body = r.json().get("data", r.json())
            items = body if isinstance(body, list) else [body]
            link = next((i.get("link") or i.get("url") for i in items if isinstance(i, dict)), None)
            if not link:
                raise BlingError(f"Resposta de etiqueta inesperada: {r.text[:200]}")
            return self.download(link)
        return r.content
