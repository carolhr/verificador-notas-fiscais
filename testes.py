from validadores import calcular_dv_chave, chave_valida

# 43 caracteres, com letras na parte do CNPJ
base = "352410" + "12ABC345000195" + "55" + "001" + "000001234" + "1" + "10000123"
print("Tamanho da base:", len(base))  # esperado: 43

chave = base + str(calcular_dv_chave(base))
print(chave_valida(chave))             # esperado: True
print(chave_valida(chave[:-1] + "9"))  # esperado: False (dígito alterado)