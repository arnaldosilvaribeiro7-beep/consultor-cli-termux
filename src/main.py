#!/usr/bin/env python3
"""Consultor CLI: consulta pública de CNPJ e validação local de CPF."""

import json
import re
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_URL = "https://brasilapi.com.br/api/cnpj/v1/{}"

REGIOES_FISCAIS = {
    "0": "Rio Grande do Sul",
    "1": "São Paulo (interior e capital)",
    "2": "São Paulo (interior e capital)",
    "3": "Paraná e Santa Catarina",
    "4": "Minas Gerais",
    "5": "Bahia e Sergipe",
    "6": "Rio de Janeiro e Espírito Santo",
    "7": "Alagoas, Pernambuco, Paraíba, Rio Grande do Norte e Ceará",
    "8": "Acre, Amazonas, Amapá, Pará, Rondônia e Roraima",
    "9": "Goiás, Mato Grosso, Mato Grosso do Sul e Distrito Federal",
}


def only_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def format_cnpj(value: str) -> str:
    digits = only_digits(value)
    if len(digits) != 14:
        return value
    return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"


def format_cpf(value: str) -> str:
    digits = only_digits(value)
    if len(digits) != 11:
        return value
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


def validar_cpf(cpf: str) -> bool:
    digits = only_digits(cpf)
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


def consultar_cnpj(cnpj: str, timeout: int = 15) -> dict[str, Any]:
    digits = only_digits(cnpj)
    if len(digits) != 14:
        raise ValueError("CNPJ deve conter 14 dígitos.")
    request = Request(API_URL.format(digits), headers={"User-Agent": "consultor-cli/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            raise RuntimeError("CNPJ não encontrado na base consultada.") from exc
        raise RuntimeError(f"A API respondeu com HTTP {exc.code}.") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError("Não foi possível acessar a API pública. Verifique a internet.") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("A resposta da API não está em formato válido.") from exc
    if not isinstance(data, dict):
        raise RuntimeError("A API retornou um formato inesperado.")
    return data


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


def exibir_cnpj(data: dict[str, Any]) -> None:
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
    print_field("QSA (nome | qualificação | faixa etária)", qsa)
    print("\nLOCALIZAÇÃO")
    print_field("Logradouro", value(data, "logradouro"))
    print_field("Número", value(data, "numero"))
    print_field("Bairro", value(data, "bairro"))
    print_field("CEP", value(data, "cep"))
    print_field("Município", value(data, "municipio"))
    print_field("UF", value(data, "uf"))
    print("\nCONTATO COMERCIAL CADASTRADO")
    print_field("E-mail", value(data, "email"))
    print_field("Telefone", value(data, "ddd_telefone_1", "telefone"))
    print("\nFonte: BrasilAPI (dados públicos de CNPJ). A disponibilidade e atualização dependem da fonte.")


def consultar_cpf() -> None:
    cpf = input("Digite o CPF (com ou sem pontos/traço): ").strip()
    digits = only_digits(cpf)
    print("\n" + "=" * 64)
    print("VALIDAÇÃO DE CPF")
    print("=" * 64)
    print_field("CPF formatado", format_cpf(digits))
    print_field("Quantidade de dígitos", len(digits))
    print_field("Dígitos verificadores", "Válidos pelo algoritmo módulo 11" if validar_cpf(digits) else "Inválidos")
    if len(digits) == 11:
        print_field("Região fiscal associada ao 9º dígito", REGIOES_FISCAIS.get(digits[8], "Não identificada"))
    else:
        print_field("Região fiscal associada ao 9º dígito", "Indisponível: CPF incompleto")
    print("\nAVISO DE PRIVACIDADE")
    print("Este programa não consulta nome, endereço, situação cadastral ou qualquer base privada de CPF.")
    print("A validação é local; o número não é enviado pela opção CPF. A região fiscal é apenas uma")
    print("associação histórica do 9º dígito e não revela localização atual. Use dados pessoais somente")
    print("com base legal e finalidade legítima, observando a LGPD (Lei nº 13.709/2018).")


def menu() -> None:
    print("\nCONSULTOR-CLI | CNPJ e CPF | Termux")
    print("Consultas responsáveis com fontes públicas e limites de privacidade.")
    while True:
        print("\nO que você deseja consultar/validar?")
        print("1 - CNPJ | 2 - CPF | 0 - Sair")
        choice = input("Escolha: ").strip()
        if choice == "0":
            print("Até logo.")
            return
        if choice == "1":
            try:
                cnpj = input("Digite o CNPJ: ").strip()
                exibir_cnpj(consultar_cnpj(cnpj))
            except (ValueError, RuntimeError) as exc:
                print(f"\nErro: {exc}")
        elif choice == "2":
            consultar_cpf()
        else:
            print("Opção inválida. Escolha 1, 2 ou 0.")
        input("\nPressione Enter para voltar ao menu...")


if __name__ == "__main__":
    try:
        menu()
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrado.")
        sys.exit(0)
