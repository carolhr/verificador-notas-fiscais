def limpar_cnpj(cnpj):
    # Remove pontos, barra e traço, deixando só letras e números
    return "".join(c for c in cnpj.upper() if c.isalnum())


def calcular_digito(base, pesos):
    soma = 0
    for caractere, peso in zip(base, pesos):
        valor = ord(caractere) - 48  # número vale ele mesmo; letra também tem valor
        soma += valor * peso
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def cnpj_valido(cnpj):
    cnpj = limpar_cnpj(cnpj)

    if len(cnpj) != 14:
        return False
    if cnpj == cnpj[0] * 14:  # ex.: 00000000000000
        return False

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1

    d1 = calcular_digito(cnpj[:12], pesos1)
    d2 = calcular_digito(cnpj[:12] + str(d1), pesos2)

    return cnpj[12:] == f"{d1}{d2}"


def limpar_chave(chave):
    # Mantém letras (A-Z) e números; remove espaços e símbolos
    return "".join(c for c in chave.upper() if c.isascii() and c.isalnum())


def calcular_dv_chave(base43):
    pesos = [2, 3, 4, 5, 6, 7, 8, 9]
    soma = 0
    # Percorre da direita para a esquerda
    for posicao, caractere in enumerate(reversed(base43)):
        peso = pesos[posicao % 8]
        valor = ord(caractere) - 48  # número vale ele mesmo; letra também tem valor
        soma += valor * peso
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def chave_valida(chave):
    chave = limpar_chave(chave)

    if len(chave) != 44:
        return False

    dv_calculado = calcular_dv_chave(chave[:43])
    return chave[43] == str(dv_calculado)