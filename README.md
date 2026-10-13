# Verificador de Notas Fiscais

Ferramenta gratuita, escrita em Python, que recebe notas fiscais eletrônicas (NF-e) em **XML** ou **PDF (DANFE)** e devolve uma lista dos possíveis erros encontrados.

Tudo roda no seu próprio computador: os arquivos das notas **não são enviados para a internet** e nenhum serviço pago é necessário.

> **Aviso:** a ferramenta é um apoio para encontrar inconsistências. Ela **não consulta a SEFAZ**, então não confirma se a nota está autorizada ou se existe oficialmente.

## O que é verificado

- **Chave de acesso:** 44 caracteres e dígito verificador correto (inclusive com CNPJ alfanumérico)
- **CNPJ do emitente:** dígitos verificadores corretos
- **CNPJ x chave:** o CNPJ da nota é o mesmo que está dentro da chave de acesso
- **Itens:** quantidade × valor unitário = valor do item
- **Soma dos itens:** bate com o total de produtos
- **Valor total da nota:** produtos − descontos + frete + seguro + outras despesas + impostos

## Requisitos

- Python 3.10 ou superior (python.org; no Windows, marque **Add Python to PATH** na instalação)
- Bibliotecas `pdfplumber` e `streamlit`

## Instalação

```bash
git clone https://github.com/carolhr/verificador-notas-fiscais.git
cd verificador-notas-fiscais
python -m pip install pdfplumber streamlit
```

> No Windows, use sempre `python -m pip` em vez de só `pip`. Avisos sobre pastas "not on PATH" durante a instalação podem ser ignorados.

## Como usar

### Pela tela (recomendado)

```bash
python -m streamlit run app.py
```

O navegador abre em `http://localhost:8501`. Envie uma ou várias notas (XML ou PDF) e veja os erros de cada arquivo. Para encerrar, aperte `Ctrl+C` no terminal.

### Pela pasta de notas (sem tela)

1. Coloque os arquivos `.xml` e `.pdf` dentro da pasta `notas/`
2. Rode:

```bash
python main.py
```

Exemplo de saída:

```
=== nota_com_erro.xml ===
4 erro(s) encontrado(s):
[GRAVE] cnpj_emitente: CNPJ do emitente inválido: 11222333000182
[GRAVE] item 2 (Caneta): 20.0000 x 2.50 = 50.00, mas a nota informa 55.00.

=== nota_exemplo.xml ===
Nenhum erro encontrado.
```

## Estrutura do projeto

| Arquivo | Função |
|---|---|
| `app.py` | Tela (Streamlit) para enviar as notas e ver os erros |
| `main.py` | Versão sem tela: lê a pasta `notas/` e mostra os erros no terminal |
| `leitor.py` | Escolhe o leitor conforme o tipo do arquivo (XML ou PDF) |
| `leitor_xml.py` | Leitura de notas em XML |
| `leitor_pdf.py` | Leitura de notas em PDF (DANFE): chave, totais e itens |
| `validadores.py` | Validação de CNPJ e da chave de acesso |
| `regras.py` | Regras de verificação e lista de erros |

## Limitações conhecidas

- **PDFs escaneados ou fotos** ainda não são lidos (é preciso que o PDF tenha texto selecionável)
- **Layout do DANFE:** a leitura de itens e totais do PDF foi testada com um modelo de DANFE; outros layouts podem mostrar o aviso de que itens e totais não foram verificados. Quando possível, prefira o **XML**
- Foco em **NF-e de produtos** (modelo 55); notas de serviço municipais (NFS-e) não são suportadas
- Sem consulta à SEFAZ

## Problemas comuns

| Problema | Solução |
|---|---|
| `pip` não é reconhecido | Use `python -m pip install ...` |
| `ModuleNotFoundError` | Rode `python -m pip install pdfplumber streamlit` |
| `FileNotFoundError` | Confira o nome do arquivo e se o terminal está dentro da pasta do projeto |
| A página não abre | Copie o endereço `Local URL` que aparece no terminal e cole no navegador |
| "Nenhuma chave de acesso válida foi encontrada" (PDF) | O PDF pode ser escaneado ou a chave estar ilegível; tente usar o XML |

## Cuidados com dados reais

Notas fiscais contêm CNPJ, nomes, endereços e valores. **Não publique notas reais** neste repositório, em *issues* ou em prints. A pasta `notas/` está no `.gitignore` para evitar envios por engano.

## Próximos passos

- Leitura de PDFs escaneados com OCR gratuito
- Relatório dos erros para baixar (CSV ou PDF)
- Mais regras: campos obrigatórios, datas, itens duplicados, conferência de impostos
- Suporte a mais modelos de DANFE

Um tutorial completo, com mais detalhes, está em `docs/Tutorial_Verificador_Notas_Fiscais.docx`.
