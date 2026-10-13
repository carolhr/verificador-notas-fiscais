import re
from leitor_pdf import extrair_texto_pdf

caminho = "notas/nota-obramax.pdf"   # troque pelo nome do seu PDF
linhas = extrair_texto_pdf(caminho).splitlines()

for i, linha in enumerate(linhas[29:60], start=30):
    print(i, re.sub(r"\d", "9", linha))