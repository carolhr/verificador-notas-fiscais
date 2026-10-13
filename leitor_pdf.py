import re
from collections import defaultdict

import pdfplumber

from validadores import chave_valida


def extrair_texto_pdf(caminho):
    # Junta o texto de todas as páginas do PDF
    paginas = []
    with pdfplumber.open(caminho) as pdf:
        for pagina in pdf.pages:
            paginas.append(pagina.extract_text() or "")
    return "\n".join(paginas)


def achar_chave(texto):
    # Busca simples no texto (funciona quando não há sobreposição)
    achado = re.search(r"(?:\d{4}\s*){11}", texto)
    if achado is None:
        return None
    return "".join(c for c in achado.group() if c.isdigit())


def agrupar_digitos(pagina):
    # Agrupa os dígitos da página por fonte, tamanho e altura
    grupos = defaultdict(list)
    for c in pagina.chars:
        if c["text"].isdigit():
            grupo = (c["fontname"], round(c["size"], 1), round(c["top"]))
            grupos[grupo].append(c)
    return grupos


def achar_chave_no_pdf(caminho):
    # Olha cada caractere e sua posição, em vez do texto já misturado
    with pdfplumber.open(caminho) as pdf:
        for pagina in pdf.pages:
            for chars in agrupar_digitos(pagina).values():
                chars.sort(key=lambda c: c["x0"])  # ordem da esquerda p/ direita
                digitos = "".join(c["text"] for c in chars)
                if len(digitos) == 44 and chave_valida(digitos):
                    return digitos
    return None


def diagnosticar_grupos(caminho):
    # Mostra só informações de formato (sem os números) para investigar
    with pdfplumber.open(caminho) as pdf:
        for n, pagina in enumerate(pdf.pages, start=1):
            for (fonte, tamanho, topo), chars in agrupar_digitos(pagina).items():
                if len(chars) >= 10:
                    print(f"pág {n} | fonte {fonte} | tamanho {tamanho} | topo {topo} | {len(chars)} dígitos")

PADRAO_ITEM = re.compile(
    r"^(\S+)\s+(.+?)\s+(\d{4}\.\d{2}\.\d{2}|\d{8})\s+\d{2,3}\s+\d{4}\s+[A-Za-z]{1,4}"
    r"\s+(\d[\d.]*,\d+)\s+(\d[\d.]*,\d+)\s+(\d[\d.]*,\d+)"
)


def numero_br(texto):
    # "1.234,56" vira "1234.56"
    return texto.replace(".", "").replace(",", ".")


def numeros_da_linha(linha):
    return re.findall(r"\d[\d.]*,\d+", linha)


def achar_linha(linhas, *trechos):
    # Posição da primeira linha que contém todos os trechos
    for i, linha in enumerate(linhas):
        if all(t in linha for t in trechos):
            return i
    return None


def ler_totais_pdf(linhas):
    totais = {}

    i = achar_linha(linhas, "VALOR TOTAL PRODUTOS")
    if i is None or i + 1 >= len(linhas):
        return None
    valores = numeros_da_linha(linhas[i + 1])
    if len(valores) != 5:
        return None
    totais["vST"] = numero_br(valores[3])
    totais["vProd"] = numero_br(valores[4])

    j = achar_linha(linhas, "VALOR DO FRETE", "VALOR TOTAL DA NF")
    if j is None or j + 1 >= len(linhas):
        return None
    valores = numeros_da_linha(linhas[j + 1])
    if len(valores) != 6:
        return None
    nomes = ["vFrete", "vSeg", "vDesc", "vOutro", "vIPI", "vNF"]
    for nome, valor in zip(nomes, valores):
        totais[nome] = numero_br(valor)

    return totais


def ler_itens_pdf(linhas):
    inicio = achar_linha(linhas, "DADOS DOS PRODUTOS")
    fim = achar_linha(linhas, "CÁLCULO DO ISSQN")
    if inicio is None or fim is None:
        return None

    itens = []
    for linha in linhas[inicio:fim]:
        achado = PADRAO_ITEM.match(linha)
        if achado:
            itens.append({
                "descricao": achado.group(2),
                "quantidade": numero_br(achado.group(4)),
                "valor_unitario": numero_br(achado.group(5)),
                "valor_total": numero_br(achado.group(6)),
            })
    return itens or None


def ler_nota_pdf(caminho):
    chave = achar_chave_no_pdf(caminho)
    if chave is None:
        raise ValueError(
            "Nenhuma chave de acesso válida foi encontrada "
            "(ela pode estar ausente, ilegível ou com dígito verificador incorreto)."
        )

    linhas = extrair_texto_pdf(caminho).splitlines()
    totais = ler_totais_pdf(linhas)
    itens = ler_itens_pdf(linhas)

    return {
        "chave": chave,
        "numero": str(int(chave[25:34])),   # número da nota dentro da chave
        "cnpj_emitente": chave[6:20],       # CNPJ do emitente dentro da chave
        "nome_emitente": None,
        "valor_total_nota": totais["vNF"] if totais else None,
        "totais": totais,
        "itens": itens,
    }