import os
import re
from downloader import PASTA_JOGOS

FORMATOS_VALIDOS = (".iso", ".bin", ".img", ".mdf", ".nrg", ".gz", ".chd", ".cso",".cue")

def deletar_jogo(nome_base):
    """
    Deleta todos os arquivos do jogo que contenham o nome_base no nome do arquivo e
    terminem com uma das extensões válidas.
    """
    arquivos_removidos = []

    # Gera padrão de comparação flexível (ignora parênteses, versões, idiomas, etc)
    padrao = re.compile(re.escape(nome_base), re.IGNORECASE)

    for root, _, arquivos in os.walk(PASTA_JOGOS):
        for arquivo in arquivos:
            if arquivo.lower().endswith(FORMATOS_VALIDOS) and padrao.search(arquivo):
                caminho = os.path.join(root, arquivo)
                try:
                    os.remove(caminho)
                    arquivos_removidos.append(arquivo)
                except Exception as e:
                    print(f"Erro ao remover {arquivo}: {e}")

    return arquivos_removidos
