import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
import os
import zipfile
import subprocess

try:
    import py7zr
except ImportError:
    py7zr = None


NUPKG_URL = "https://community.chocolatey.org/api/v2/package/pcsx2.portable/2.6.3"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_PCSX2 = os.path.join(BASE_DIR, "pcsx2")
PCSX2_EXE = os.path.join(PASTA_PCSX2, "pcsx2-qt.exe")


# =========================
# JANELA DE AVISO
# =========================
class AvisoConfiguracaoPCSX2(tk.Toplevel):

    def __init__(self, master=None):
        super().__init__(master)
 
        self.title("Configuração inicial do PCSX2")
        self.geometry("520x320")
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self.fechar_e_abrir)

        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        texto = (
            "PCSX2 instalado com sucesso!\n\n"
            "Agora você precisa fazer a configuração inicial.\n\n"
            "IMPORTANTE:\n"
            "Durante a configuração selecione a pasta:\n\n"
            "   jogos\n\n"
            "que está dentro da pasta do PSLoad.\n\n"
            "PASSOS:\n"
            "1 - Feche esta janela\n"
            "2 - Faça a configuração inicial do PCSX2\n"
            "3 - Selecione a pasta 'jogos'\n"
            "4 - Após terminar feche o PCSX2\n"
            "5 - Volte para o PSLoad\n"
        )

        label = tk.Label(
            frame,
            text=texto,
            justify="left",
            wraplength=460
        )
        label.pack(pady=20)

        btn = tk.Button(
            frame,
            text="Abrir PCSX2",
            font=("Arial", 11, "bold"),
            command=self.fechar_e_abrir
        )
        btn.pack(pady=10)

    def fechar_e_abrir(self):

        self.destroy()

        if os.path.exists(PCSX2_EXE):
            subprocess.Popen([PCSX2_EXE])
        else:
            messagebox.showerror(
                "Erro",
                "PCSX2 não encontrado."
            )
# =========================
# INSTALADOR
# =========================
class InstaladorPCSX2(tk.Toplevel):

    def __init__(self, master=None):
        super().__init__(master)

        self.title("Instalador PCSX2")
        self.geometry("420x180")
        self.resizable(False, False)

        tk.Label(
            self,
            text="Instalar PCSX2 automaticamente"
        ).pack(pady=10)

        self.label_progresso = tk.Label(self, text="")
        self.label_progresso.pack()

        self.progressbar = ttk.Progressbar(
            self,
            orient="horizontal",
            length=380,
            mode="determinate"
        )
        self.progressbar.pack(pady=10)

        self.btn_iniciar = tk.Button(
            self,
            text="Instalar PCSX2",
            command=self.iniciar_instalacao
        )
        self.btn_iniciar.pack(pady=5)

    def iniciar_instalacao(self):

        self.btn_iniciar.config(state="disabled")

        threading.Thread(
            target=self.baixar_e_extrair,
            daemon=True
        ).start()

    def baixar_e_extrair(self):

        try:

            if os.path.exists(PCSX2_EXE):

                self.master.after(
                    0,
                    lambda: messagebox.showinfo(
                        "PCSX2",
                        "PCSX2 já está instalado."
                    )
                )

                self.master.after(0, self.destroy)
                return

            os.makedirs(PASTA_PCSX2, exist_ok=True)

            self.label_progresso.config(
                text="Baixando pacote PCSX2..."
            )

            resp = requests.get(NUPKG_URL, stream=True)
            resp.raise_for_status()

            tamanho_total = int(resp.headers.get("content-length", 0))
            baixado = 0

            nupkg_path = os.path.join(
                PASTA_PCSX2,
                "pcsx2_portable.nupkg"
            )

            with open(nupkg_path, "wb") as f:

                for dados in resp.iter_content(8192):

                    if not dados:
                        continue

                    f.write(dados)
                    baixado += len(dados)

                    self.progressbar["value"] = baixado
                    self.progressbar["maximum"] = tamanho_total

                    self.update_idletasks()

            self.label_progresso.config(text="Extraindo pacote...")

            with zipfile.ZipFile(nupkg_path, "r") as zip_ref:
                zip_ref.extractall(PASTA_PCSX2)

            tools_dir = os.path.join(PASTA_PCSX2, "tools")

            arquivo_7z = None

            for arq in os.listdir(tools_dir):
                if arq.lower().endswith(".7z"):
                    arquivo_7z = os.path.join(tools_dir, arq)
                    break

            if not arquivo_7z:

                self.master.after(
                    0,
                    lambda: messagebox.showerror(
                        "Erro",
                        "Arquivo portátil não encontrado."
                    )
                )
                return

            self.label_progresso.config(text="Extraindo PCSX2...")

            self.progressbar.config(mode="indeterminate")
            self.progressbar.start()

            if py7zr:

                with py7zr.SevenZipFile(arquivo_7z, mode="r") as z:
                    z.extractall(path=PASTA_PCSX2)

            else:

                self.master.after(
                    0,
                    lambda: messagebox.showerror(
                        "Erro",
                        "py7zr não instalado.\nUse:\npip install py7zr"
                    )
                )
                return

            self.progressbar.stop()

            self.progressbar.config(
                mode="determinate",
                value=100
            )

            self.label_progresso.config(
                text="Instalação concluída!"
            )

            try:
                os.remove(nupkg_path)
            except:
                pass

            # mensagem de sucesso
            self.master.after(
                0,
                lambda: messagebox.showinfo(
                    "Sucesso",
                    "PCSX2 instalado com sucesso!"
                )
            )

            # fechar instalador
            self.master.after(0, self.destroy)

            # abrir aviso
            self.master.after(
                0,
                lambda: AvisoConfiguracaoPCSX2(self.master)
            )

        except Exception as e:

            self.master.after(
                0,
                lambda: messagebox.showerror(
                    "Erro",
                    f"Erro na instalação:\n{e}"
                )
            )

            self.master.after(0, self.destroy)


# =========================
# FUNÇÃO PARA CHAMAR
# =========================
def instalar_pcsx2_thread(master=None):
    InstaladorPCSX2(master)


# =========================
# TESTE
# =========================
if __name__ == "__main__":

    root = tk.Tk()
    root.title("PSLoad")
    root.geometry("300x200")

    btn = tk.Button(
        root,
        text="Instalar PCSX2",
        command=lambda: instalar_pcsx2_thread(root)
    )
    btn.pack(expand=True)

    root.mainloop()