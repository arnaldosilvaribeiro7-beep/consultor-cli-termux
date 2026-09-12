"""Normalização e validação de identificadores empresariais."""

import re


def sanitizar_documento(entrada: str) -> str:
    """Remove tudo que não seja dígito antes de qualquer validação ou requisição."""
    return re.sub(r"\D", "", entrada or "")


def validar_tamanho_cnpj(entrada: str) -> str:
    """Sanitiza e valida o CNPJ, retornando somente os 14 dígitos."""
    cnpj = sanitizar_documento(entrada)
    if len(cnpj) != 14:
        raise ValueError("CNPJ deve conter exatamente 14 dígitos após a limpeza.")
    return cnpj


def validar_tamanho_cep(entrada: str) -> str:
    """Sanitiza e valida CEP, retornando somente os 8 dígitos."""
    cep = sanitizar_documento(entrada)
    if len(cep) != 8:
        raise ValueError("CEP deve conter exatamente 8 dígitos após a limpeza.")
    return cep
