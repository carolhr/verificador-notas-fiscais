from decimal import Decimal, InvalidOperation
from validadores import cnpj_valido, chave_valida, limpar_cnpj


def para_decimal(valor):
    # Converte texto em número exato (Decimal evita erros de arredondamento do float)
    try:
        return Decimal(valor)
    except (InvalidOperation, TypeError):
        return None


def erro(gravidade, campo, mensagem):
    return {"gravidade": gravidade, "campo": campo, "mensagem": mensagem}


def valor_ou_zero(totais, campo):
    # Campo que não aparece na nota conta como zero
    texto = totais.get(campo)
    if texto is None:
        return Decimal("0")
    return para_decimal(texto)


def verificar_nota(nota):
    erros = []

    # 1) Chave de acesso
    chave = nota["chave"]
    if not chave_valida(chave):
        erros.append(erro("grave", "chave", "Chave de acesso inválida (tamanho ou dígito verificador)."))

    # 2) CNPJ do emitente
    cnpj = nota["cnpj_emitente"] or ""
    if not cnpj_valido(cnpj):
        erros.append(erro("grave", "cnpj_emitente", f"CNPJ do emitente inválido: {cnpj}"))

    # 3) CNPJ da nota x CNPJ dentro da chave (posições 7 a 20 da chave)
    if len(chave) == 44 and limpar_cnpj(cnpj) != chave[6:20]:
        erros.append(erro("grave", "cnpj_emitente", "O CNPJ do emitente é diferente do CNPJ contido na chave de acesso."))
    # Notas lidas de PDF ainda não trazem itens e totais
    if nota["itens"] is None or nota["totais"] is None:
        erros.append(erro(
            "aviso", "itens e totais",
            "Itens e totais não foram verificados (a leitura de PDF ainda não extrai esses campos)."
        ))
        return erros


    # 4) Cálculo de cada item: quantidade x valor unitário = valor do item
    soma_itens = Decimal("0")
    for i, item in enumerate(nota["itens"], start=1):
        qtd = para_decimal(item["quantidade"])
        unitario = para_decimal(item["valor_unitario"])
        total_item = para_decimal(item["valor_total"])

        if qtd is None or unitario is None or total_item is None:
            erros.append(erro("grave", f"item {i}", "Quantidade ou valores ausentes ou ilegíveis."))
            continue

        esperado = (qtd * unitario).quantize(Decimal("0.01"))
        if esperado != total_item:
            erros.append(erro(
                "grave", f"item {i} ({item['descricao']})",
                f"{qtd} x {unitario} = {esperado}, mas a nota informa {total_item}."
            ))
        soma_itens += total_item

    # 5) Soma dos itens x valor dos produtos informado nos totais
    totais = nota["totais"]
    vprod = para_decimal(totais["vProd"])
    if vprod is None:
        erros.append(erro("grave", "total vProd", "Valor total dos produtos ausente ou ilegível."))
    elif soma_itens != vprod:
        erros.append(erro(
            "grave", "total vProd",
            f"A soma dos itens é {soma_itens}, mas o total de produtos informado é {vprod}."
        ))

    # 6) Valor final da nota = produtos - descontos + frete + seguro + outras despesas + impostos
    nomes = ["vProd", "vDesc", "vICMSDeson", "vST", "vFCPST", "vFrete",
             "vSeg", "vOutro", "vII", "vIPI", "vIPIDevol"]
    v = {nome: valor_ou_zero(totais, nome) for nome in nomes}
    vnf = para_decimal(totais["vNF"])

    if vnf is None or any(valor is None for valor in v.values()):
        erros.append(erro("grave", "total vNF", "Algum valor dos totais está ausente ou ilegível."))
    else:
        esperado = (v["vProd"] - v["vDesc"] - v["vICMSDeson"] + v["vST"] + v["vFCPST"]
                    + v["vFrete"] + v["vSeg"] + v["vOutro"] + v["vII"] + v["vIPI"] + v["vIPIDevol"])
        if esperado != vnf:
            erros.append(erro(
                "grave", "total vNF",
                f"Pelos componentes, o total deveria ser {esperado}, mas a nota informa {vnf}."
            ))

    return erros