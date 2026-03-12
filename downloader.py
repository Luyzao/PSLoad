import os
import zipfile
import gdown
import subprocess
import sys
import io
from tkinter import messagebox
from igdb_api import baixar_capa
from utils import atualizar_lista_baixados


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PASTA_JOGOS = os.path.join(BASE_DIR, "jogos")

os.makedirs(PASTA_JOGOS, exist_ok=True)


class StdoutRedirector(io.StringIO):

    def __init__(self, update_callback):
        super().__init__()
        self.update_callback = update_callback
        self.buffer = ""

    def write(self, s):
        self.buffer += s

        if "\r" in s or "\n" in s:
            self.update_callback(self.buffer.strip())
            self.buffer = ""

    def flush(self):
        pass


def baixar_com_gdown(file_id, destino, update_callback=None, nome=""):

    url = f"https://drive.google.com/uc?id={file_id}"

    comando = [
        sys.executable, "-m", "gdown", url,
        "--output", destino,
        "--no-cookies"
    ]

    processo = subprocess.Popen(
        comando,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        encoding="utf-8",
        errors="ignore",
        bufsize=1
    )

    for linha in processo.stdout:

        if update_callback:
            update_callback(f"{nome} (Baixando... {linha.strip()})")

    processo.wait()


def baixar_e_descompactar(jogo, update_status_callback):

    try:

        nome = jogo["nome"]
        file_id = jogo["id"]

        zip_path = os.path.join(PASTA_JOGOS, f"{nome}.zip")

        update_status_callback(f"{nome} (Iniciando...)")

        baixar_com_gdown(file_id, zip_path, update_status_callback, nome)

        update_status_callback(f"{nome} (Extraindo...)")

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:

            total_arquivos = len(zip_ref.infolist())

            for i, file in enumerate(zip_ref.infolist(), 1):

                porcentagem = int(100 * i / total_arquivos)

                update_status_callback(f"{nome} (Extraindo... {porcentagem}%)")

                zip_ref.extract(file, PASTA_JOGOS)

        os.remove(zip_path)

        # mover ISO para pasta principal
        for root_dir, _, files in os.walk(PASTA_JOGOS):

            for file in files:

                caminho_atual = os.path.join(root_dir, file)
                caminho_destino = os.path.join(PASTA_JOGOS, file)

                if file.endswith(".iso") and not os.path.samefile(root_dir, PASTA_JOGOS):

                    if not os.path.exists(caminho_destino):
                        os.rename(caminho_atual, caminho_destino)

        update_status_callback(f"{nome} (Pronto)")

        atualizar_lista_baixados()

        capa_path = os.path.join(BASE_DIR, "capas", f"{nome}.jpg")

        if not os.path.exists(capa_path):
            baixar_capa(nome)

    except Exception as e:

        update_status_callback(f"{jogo['nome']} (Erro)")

        messagebox.showerror(
            "Erro",
            f"Erro ao baixar {jogo['nome']}: {e}"
        )