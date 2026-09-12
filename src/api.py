"""Integração com a API pública de CNPJ."""

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from validators import validar_tamanho_cnpj

API_URL = "https://brasilapi.com.br/api/cnpj/v1/{}"


def consultar_cnpj(cnpj: str, timeout: int = 15) -> dict[str, Any]:
    """Consulta CNPJ formatado ou numérico, enviando somente 14 dígitos."""
    digits = validar_tamanho_cnpj(cnpj)
    request = Request(API_URL.format(digits), headers={"User-Agent": "consultor-cli/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code in (400, 404):
            raise RuntimeError("CNPJ não encontrado ou formato inválido.") from exc
        if exc.code >= 500:
            raise RuntimeError("A API pública está temporariamente indisponível. Tente novamente mais tarde.") from exc
        raise RuntimeError(f"Não foi possível consultar o CNPJ (HTTP {exc.code}).") from exc
    except (URLError, TimeoutError):
        raise RuntimeError("Não foi possível acessar a API pública. Verifique a internet.")
    except json.JSONDecodeError as exc:
        raise RuntimeError("A resposta da API não está em formato válido.") from exc
    if not isinstance(data, dict):
        raise RuntimeError("A API retornou um formato inesperado.")
    return data
