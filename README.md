# Consultor CLI (Termux)

CLI interativo, simples e responsável para consultar dados públicos de **CNPJ** e validar um **CPF localmente**. O projeto foi desenhado para iniciar com `python src/main.py` ou com o atalho `./run.sh`, sem argumentos obrigatórios.

## Instalação e execução

No Termux, instale o Python uma vez e clone o repositório:

```bash
pkg update -y && pkg install python git -y
git clone https://github.com/SEU_USUARIO/consultor-cli-termux.git
cd consultor-cli-termux
chmod +x run.sh
./run.sh
```

O menu oferece:

1. **CNPJ**: consulta a BrasilAPI e exibe identificação, situação cadastral, datas, CNAEs, QSA, porte, capital social, endereço e contatos comerciais retornados pela fonte.
2. **CPF**: remove pontuação, valida os dois dígitos verificadores pelo algoritmo módulo 11 e mostra a associação histórica do 9º dígito com a região fiscal. Nenhum CPF é enviado à internet nessa opção.

## Privacidade, legalidade e limitações

Este projeto não é uma ferramenta de investigação de pessoas. Não faz busca nominal de CPF, não tenta contornar autenticação, não acessa bases vazadas e não promete dados além dos disponibilizados publicamente pela fonte consultada. A utilização de dados pessoais deve ter finalidade legítima e base legal, em conformidade com a **Lei de Acesso à Informação (LAI)**, a **LGPD (Lei nº 13.709/2018)** e os termos das fontes utilizadas.

A consulta de CNPJ depende de internet e da disponibilidade da [BrasilAPI](https://brasilapi.com.br/). Os campos podem mudar conforme a resposta da API. A associação regional do CPF é uma referência histórica do 9º dígito; não indica residência ou localização atual.

## Desenvolvimento

O projeto não exige bibliotecas externas: `requirements.txt` existe para manter o fluxo de instalação uniforme no Termux. Para executar uma verificação rápida:

```bash
python -m py_compile src/main.py
printf '2\n529.982.247-25\n\n0\n' | python src/main.py
```

## Licença

Distribuído sob a licença MIT. Consulte `LICENSE`.
