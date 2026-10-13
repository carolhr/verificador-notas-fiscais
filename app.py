import tempfile
from pathlib import Path

import streamlit as st

from leitor import ler_nota
from regras import verificar_nota

st.set_page_config(page_title="Verificador de Notas Fiscais")

st.title("Verificador de Notas Fiscais")
st.write("Envie uma ou mais notas (XML ou PDF) e veja os possíveis erros.")

arquivos = st.file_uploader(
    "Selecione os arquivos",
    type=["xml", "pdf"],
    accept_multiple_files=True,
)

for arquivo in arquivos:
    st.subheader(arquivo.name)

    # O leitor trabalha com arquivos em disco, então guardamos uma cópia temporária
    with tempfile.TemporaryDirectory() as pasta:
        caminho = Path(pasta) / Path(arquivo.name).name
        caminho.write_bytes(arquivo.getvalue())

        try:
            nota = ler_nota(caminho)
            erros = verificar_nota(nota)
        except Exception as e:
            st.error(f"Não foi possível ler este arquivo: {e}")
            continue

    if not erros:
        st.success("Nenhum erro encontrado.")
    else:
        st.warning(f"{len(erros)} problema(s) encontrado(s):")
        for e in erros:
            texto = f"**{e['campo']}**: {e['mensagem']}"
            if e["gravidade"] == "grave":
                st.error(texto)
            else:
                st.info(texto)