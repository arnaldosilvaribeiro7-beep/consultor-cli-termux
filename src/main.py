#!/usr/bin/env python3
"""Consultor CLI: consulta pública de CNPJ e enriquecimento postal por CEP."""

import sys
from typing import Any

from api import consultar_cep, consultar_cnpj
from validators import sanitizar_documento


def format_cnpj(value: str) -> str:
    digits = sanitizar_documento(value)
    if len(digits) != 14:
        return value
    return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"


def format_cep(value: str) -> str:
    digits = sanitizar_documento(value)
    if len(digits) != 8:
        return value
    return f"{digits[:5]}-{digits[5:]}"


def value(data: dict[str, Any], *keys: str, default="Não informado") -> Any:
    for key in keys:
        current = data.get(key)
        if current not in (None, "", [], {}):
            return current
    return default


def print_field(label: str, content: Any) -> None:
    if isinstance(content, list):
        if not content:
            print(f"{label}: Não informado")
        else:
            print(f"{label}:")
            for item in content:
                print(f"  - {item}")
    else:
        print(f"{label}: {content}")


def enriquecer_por_cep(data: dict[str, Any]) -> dict[str, Any] | None:
    """Consulta dados postais públicos usando o CEP já retornado para a empresa."""
    cep = value(data, "cep", default="")
    cep_digits = sanitizar_documento(str(cep))
    if len(cep_digits) != 8:
        print("\nEnriquecimento postal: não executado, pois o CNPJ não retornou um CEP válido.")
        return None
    try:
        postal = consultar_cep(cep_digits)
    except (ValueError, RuntimeError) as exc:
        print(f"\nEnriquecimento postal indisponível: {exc}")
        return None
    return postal


def exibir_cnpj(data: dict[str, Any], postal: dict[str, Any] | None = None) -> None:
    print("\n" + "=" * 64)
    print("RESULTADO DA CONSULTA DE CNPJ")
    print("=" * 64)
    print_field("CNPJ", format_cnpj(str(value(data, "cnpj"))))
    print_field("Razão social", value(data, "razao_social", "nome_empresarial"))
    print_field("Nome fantasia", value(data, "nome_fantasia"))
    print_field("Matriz/filial", value(data, "identificador_matriz_filial"))
    print_field("Situação cadastral", value(data, "descricao_situacao_cadastral", "situacao_cadastral"))
    print_field("Data da situação", value(data, "data_situacao_cadastral"))
    print_field("Motivo da situação", value(data, "descricao_motivo_situacao_cadastral", "motivo_situacao_cadastral"))
    print_field("Data de abertura", value(data, "data_inicio_atividade"))
    print_field("Porte", value(data, "porte"))
    print_field("Capital social", value(data, "capital_social"))
    principal = value(data, "cnae_fiscal_descricao")
    codigo = value(data, "cnae_fiscal")
    print_field("CNAE principal", f"{codigo} - {principal}")
    secundarios = []
    for item in value(data, "cnaes_secundarios", default=[]):
        if isinstance(item, dict):
            secundarios.append(f"{item.get('codigo', 'Sem código')} - {item.get('descricao', 'Sem descrição')}")
    print_field("CNAEs secundários", secundarios)
    qsa = []
    for socio in value(data, "qsa", default=[]):
        if isinstance(socio, dict):
            qsa.append(" | ".join(str(socio.get(k, "Não informado")) for k in ("nome_socio", "qualificacao_socio", "faixa_etaria")))
    print_field("QSA público retornado pela fonte", qsa)
    print("\nENDEREÇO COMERCIAL PUBLICADO")
    print_field("Logradouro", value(data, "logradouro"))
    print_field("Número", value(data, "numero"))
    print_field("Bairro", value(data, "bairro"))
    print_field("CEP", format_cep(str(value(data, "cep"))))
    print_field("Município", value(data, "municipio"))
    print_field("UF", value(data, "uf"))
    print("\nCONTATO COMERCIAL CADASTRADO")
    print_field("E-mail", value(data, "email"))
    print_field("Telefone", value(data, "ddd_telefone_1", "telefone"))
    if postal:
        print("\nENRIQUECIMENTO POSTAL PELO CEP")
        print_field("CEP consultado", format_cep(str(value(postal, "cep"))))
        print_field("Logradouro postal", value(postal, "street", "logradouro"))
        print_field("Bairro postal", value(postal, "neighborhood", "bairro"))
        print_field("Cidade postal", value(postal, "city", "municipio"))
        print_field("Estado postal", value(postal, "state", "uf"))
        print_field("Serviço postal", value(postal, "service"))
    print("\nFontes: BrasilAPI CNPJ e BrasilAPI CEP. Dados limitados ao que as fontes públicas retornarem.")


def menu() -> None:
    print("\nCONSULTOR-CLI | CNPJ | Termux")
    print("Consulta dados públicos da empresa e enriquece o CEP comercial retornado.")
    while True:
        print("\nO que você deseja consultar?")
        print("1 - CNPJ | 0 - Sair")
        choice = input("Escolha: ").strip()
        if choice == "0":
            print("Até logo.")
            return
        if choice == "1":
            try:
                cnpj = input("Digite o CNPJ: ").strip()
                data = consultar_cnpj(cnpj)
                postal = enriquecer_por_cep(data)
                exibir_cnpj(data, postal)
            except (ValueError, RuntimeError) as exc:
                print(f"\nErro: {exc}")
        else:
            print("Opção inválida. Escolha 1 ou 0.")
        input("\nPressione Enter para voltar ao menu...")


if __name__ == "__main__":
    try:
        menu()
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrado.")
        sys.exit(0)
