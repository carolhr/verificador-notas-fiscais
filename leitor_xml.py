import xml.etree.ElementTree as ET

# Toda NF-e usa este "endereço" (namespace) nas tags
NS = {"nfe": "http://www.portalfiscal.inf.br/nfe"}


def texto(no, caminho):
    # Busca uma tag e devolve o texto dela (ou None se não existir)
    achado = no.find(caminho, NS)
    return achado.text if achado is not None else None


def ler_totais(inf):
    campos = ["vProd", "vDesc", "vICMSDeson", "vST", "vFCPST", "vFrete",
              "vSeg", "vOutro", "vII", "vIPI", "vIPIDevol", "vNF"]
    totais = {}
    for campo in campos:
        totais[campo] = texto(inf, f"nfe:total/nfe:ICMSTot/nfe:{campo}")
    return totais

def ler_nota_xml(caminho_arquivo):
    raiz = ET.parse(caminho_arquivo).getroot()
    inf = raiz.find(".//nfe:infNFe", NS)

    itens = []
    for det in inf.findall("nfe:det", NS):
        itens.append({
            "descricao": texto(det, "nfe:prod/nfe:xProd"),
            "quantidade": texto(det, "nfe:prod/nfe:qCom"),
            "valor_unitario": texto(det, "nfe:prod/nfe:vUnCom"),
            "valor_total": texto(det, "nfe:prod/nfe:vProd"),
        })

    return {
        "chave": inf.get("Id", "").replace("NFe", ""),
        "numero": texto(inf, "nfe:ide/nfe:nNF"),
        "cnpj_emitente": texto(inf, "nfe:emit/nfe:CNPJ"),
        "nome_emitente": texto(inf, "nfe:emit/nfe:xNome"),
        "valor_total_nota": texto(inf, "nfe:total/nfe:ICMSTot/nfe:vNF"),
        "totais": ler_totais(inf),
        "itens": itens,
    }