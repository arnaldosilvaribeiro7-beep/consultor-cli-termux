"""Integrações com APIs públicas de dados empresariais e postais."""

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from validators import validar_tamanho_cep, validar_tamanho_cnpj

CNPJ_API_URL = "https://brasilapi.com.br/api/cnpj/v1/{}"
CEP_API_URL = "https://brasilapi.com.br/api/cep/v2/{}"


def _get_json(url: str, timeout: int = 15) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "consultor-cli/1.1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code in (400, 404):
            raise RuntimeError("Informação não encontrada ou formato inválido.") from exc
        if exc.code >= 500:
            raise RuntimeError("A API pública está temporariamente indisponível. Tente novamente mais tarde.") from exc
        raise RuntimeError(f"Não foi possível consultar a API (HTTP {exc.code}).") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError("Não foi possível acessar a API pública. Verifique a internet.") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("A resposta da API não está em formato válido.") from exc
    if not isinstance(data, dict):
        raise RuntimeError("A API retornou um formato inesperado.")
    return data


def consultar_cnpj(cnpj: str, timeout: int = 15) -> dict[str, Any]:
    """Consulta CNPJ formatado ou numérico, enviando somente 14 dígitos."""
    digits = validar_tamanho_cnpj(cnpj)
    try:
        return _get_json(CNPJ_API_URL.format(digits), timeout)
    except RuntimeError as exc:
        if "Informação não encontrada" in str(exc):
            raise RuntimeError("CNPJ não encontrado ou formato inválido.") from exc
        raise


def consultar_cep(cep: str, timeout: int = 15) -> dict[str, Any]:
    """Consulta somente dados postais públicos derivados do endereço empresarial."""
    digits = validar_tamanho_cep(cep)
    try:
        return _get_json(CEP_API_URL.format(digits), timeout)
    except RuntimeError as exc:
        if "Informação não encontrada" in str(exc):
            raise RuntimeError("CEP não encontrado ou formato inválido.") from exc
        raise
