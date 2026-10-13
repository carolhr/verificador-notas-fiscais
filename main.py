from pathlib import Path
from leitor import ler_nota
from regras import verificar_nota

pasta = Path("notas")
arquivos = sorted(p for p in pasta.iterdir() if p.is_file())

if not arquivos:
    print("Nenhum arquivo encontrado na pasta 'notas'.")

for arquivo in arquivos:
    print(f"\n=== {arquivo.name} ===")

    try:
        nota = ler_nota(arquivo)
        erros = verificar_nota(nota)
    except Exception as e:
        print(f"Não foi possível ler este arquivo: {e}")
        continue

    if not erros:
        print("Nenhum erro encontrado.")
    else:
        print(f"{len(erros)} erro(s) encontrado(s):")
        for e in erros:
            print(f"[{e['gravidade'].upper()}] {e['campo']}: {e['mensagem']}")