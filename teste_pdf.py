from leitor_pdf import achar_chave_no_pdf, diagnosticar_grupos

caminho = "notas/nota-obramax.pdf"   # troque pelo nome do seu PDF

chave = achar_chave_no_pdf(caminho)
print("Chave encontrada e válida?", chave is not None)

if chave is None:
    print("\n--- Grupos de dígitos encontrados no PDF ---")
    diagnosticar_grupos(caminho)