from pathlib import Path
from leitor_xml import ler_nota_xml
from leitor_pdf import ler_nota_pdf


def ler_nota(caminho):
    # Escolhe o leitor certo conforme a extensão do arquivo
    extensao = Path(caminho).suffix.lower()

    if extensao == ".xml":
        return ler_nota_xml(caminho)
    if extensao == ".pdf":
        return ler_nota_pdf(caminho)

    raise ValueError(f"Formato não suportado ainda: {extensao}")