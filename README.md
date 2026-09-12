# Consultor CLI (Termux)

CLI interativo para consultar dados públicos de **CNPJ** e enriquecer automaticamente o endereço comercial por meio do **CEP retornado pela própria consulta**. O suporte a CPF foi removido.

## Instalação e execução

No Termux:

```bash
pkg update -y && pkg install python git -y
git clone https://github.com/arnaldosilvaribeiro7-beep/consultor-cli-termux.git
cd consultor-cli-termux
chmod +x run.sh
./run.sh
```

O programa apresenta apenas:

```text
1 - CNPJ | 0 - Sair
```

Depois de receber o CNPJ, o programa:

1. Remove pontos, barras, traços e espaços automaticamente.
2. Confirma que restaram exatamente 14 dígitos antes de qualquer requisição.
3. Consulta os dados públicos empresariais na BrasilAPI.
4. Usa somente o **CEP comercial retornado pela consulta do CNPJ** para consultar dados postais públicos na BrasilAPI CEP.
5. Exibe identificação, situação cadastral, CNAEs, QSA público retornado pela fonte, porte, capital social, endereço comercial, e-mail empresarial, telefones comerciais retornados pela fonte e dados postais complementares.

Entradas como `00.000.000/0001-91` e `00000000000191` são aceitas. Erros HTTP 400, 404 e 500 são convertidos em mensagens compreensíveis e não encerram o programa.

## Privacidade, legalidade e limitações

O projeto não busca CPF, telefone pessoal, titular de telefone, WhatsApp, PIX, e-mail pessoal, moradores, vizinhos, redes sociais, vazamentos, histórico de localização, processos de pessoas físicas ou bases privadas. Os telefones são apenas formatados e exibidos quando a fonte pública de CNPJ os retorna como contatos comerciais; não há busca reversa. O QSA é exibido somente quando a fonte pública de CNPJ o retorna como dado empresarial, sem tentar descobrir informações adicionais sobre os sócios.

O enriquecimento é limitado ao endereço comercial publicado pela empresa e aos dados postais do CEP. Não há geolocalização de pessoas, enriquecimento por dados sensíveis ou tentativa de contornar autenticação. A utilização de dados deve ter finalidade legítima e base legal, em conformidade com a **LGPD (Lei nº 13.709/2018)** e os termos das fontes utilizadas.

As consultas dependem da disponibilidade da [BrasilAPI](https://brasilapi.com.br/), e os campos podem mudar conforme a resposta das fontes. Um CNPJ sem CEP válido continua sendo exibido normalmente; apenas o enriquecimento postal é ignorado.

## Desenvolvimento

O projeto usa apenas a biblioteca padrão do Python. Os módulos principais são:

- `src/validators.py`: sanitização e validação de CNPJ e CEP.
- `src/api.py`: consultas públicas de CNPJ e CEP com tratamento de erros.
- `src/main.py`: menu e apresentação dos resultados.

Para validar a sintaxe:

```bash
python -m py_compile src/main.py src/api.py src/validators.py
```

## Licença

Distribuído sob a licença MIT. Consulte `LICENSE`.
