"""Validações e normalização de documentos brasileiros."""

import re


def sanitizar_documento(entrada: str) -> str:
    """Remove tudo que não seja dígito antes de qualquer validação."""
    return re.sub(r"\D", "", entrada or "")


def validar_tamanho_cnpj(entrada: str) -> str:
    """Sanitiza e valida o tamanho do CNPJ, retornando somente os dígitos."""
    cnpj = sanitizar_documento(entrada)
    if len(cnpj) != 14:
        raise ValueError("CNPJ deve conter exatamente 14 dígitos após a limpeza.")
    return cnpj


def validar_cpf(cpf: str) -> bool:
    """Valida CPF sanitizado pelo cálculo dos dois dígitos verificadores."""
    digits = sanitizar_documento(cpf)
    if len(digits) != 11 or len(set(digits)) == 1:
        return False
    total = sum(int(digit) * weight for digit, weight in zip(digits[:9], range(10, 1, -1)))
    first = (total * 10) % 11
    first = 0 if first == 10 else first
    if first != int(digits[9]):
        return False
    total = sum(int(digit) * weight for digit, weight in zip(digits[:10], range(11, 1, -1)))
    second = (total * 10) % 11
    second = 0 if second == 10 else second
    return second == int(digits[10])
