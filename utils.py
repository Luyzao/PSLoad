import os
import platform
import subprocess

PASTA_JOGOS = os.path.join(os.path.expanduser("~"), "Jogos_PS2")

def abrir_pasta():
    if platform.system() == "Windows":
        os.startfile(PASTA_JOGOS)
    elif platform.system() == "Darwin":
        subprocess.call(["open", PASTA_JOGOS])
    else:
        subprocess.call(["xdg-open", PASTA_JOGOS])

def atualizar_lista_baixados():
    pass  # Essa função será implementada de forma adequada na interface (ui.py)
