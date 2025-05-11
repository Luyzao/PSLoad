import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import json
import os
import threading

import utils  # Importa utils corretamente
from downloader import baixar_e_descompactar, PASTA_JOGOS
from igdb_api import baixar_capa

CAPAS_DIR = "capas"

def carregar_jogos():
    with open('jogos.json', 'r') as f:
        return json.load(f)

def obter_capa(nome_jogo):
    try:
        caminho = os.path.join(CAPAS_DIR, f"{nome_jogo}.jpg")
        if not os.path.exists(caminho):
            baixar_capa(nome_jogo)
        imagem = Image.open(caminho)
        imagem = imagem.resize((250, 410), Image.LANCZOS)
        return ImageTk.PhotoImage(imagem)
    except:
        return None

def iniciar_download(jogo, listbox, index):
    progresso_var = tk.StringVar(value=f"{jogo['nome']} (Iniciando...)")
    listbox.delete(index)
    listbox.insert(index, progresso_var.get())

    def update_status(texto):
        progresso_var.set(texto)
        listbox.delete(index)
        listbox.insert(index, progresso_var.get())

    def thread_func():
        baixar_e_descompactar(jogo, update_status)
        utils.atualizar_lista_baixados()
        exibir_jogos_filtrados()

    thread = threading.Thread(target=thread_func)
    thread.start()

def criar_interface():
    global lista_baixados
    global exibir_jogos_filtrados

    root = tk.Tk()
    root.title("Biblioteca de Jogos PS2")

    largura = 900
    altura = 700
    tela_largura = root.winfo_screenwidth()
    tela_altura = root.winfo_screenheight()
    x = (tela_largura - largura) // 2
    y = (tela_altura - altura) // 2
    root.geometry(f"{largura}x{altura}+{x}+{y}")
    root.resizable(False, False)

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    # ==== ABA 1: Biblioteca Online ====
    aba_biblioteca = tk.Frame(notebook)
    notebook.add(aba_biblioteca, text="Biblioteca Online")

    tk.Label(aba_biblioteca, text="Jogos Disponíveis:", font=('Arial', 14)).pack(pady=5)
    filtro_online_var = tk.StringVar()
    tk.Entry(aba_biblioteca, textvariable=filtro_online_var, font=('Arial', 12)).pack(pady=5, fill='x', padx=10)

    conteudo_frame = tk.Frame(aba_biblioteca)
    conteudo_frame.pack(expand=True, fill='both')

    listbox = tk.Listbox(conteudo_frame, font=('Arial', 12), width=30)
    listbox.pack(side="left", fill="both", expand=True, padx=10)

    scrollbar = tk.Scrollbar(conteudo_frame)
    scrollbar.pack(side="left", fill="y")
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    capa_label = tk.Label(conteudo_frame)
    capa_label.pack(side="left", padx=10, pady=10)

    jogos = carregar_jogos()
    jogos_filtrados = list(jogos)

    def exibir_jogos_filtrados():
        filtro = filtro_online_var.get().lower()
        listbox.delete(0, tk.END)
        jogos_filtrados.clear()
        for jogo in jogos:
            nome_base = jogo["nome"]
            caminho_iso = os.path.join(PASTA_JOGOS, f"{nome_base}.iso")
            nome_exibido = f"{nome_base} (baixado)" if os.path.exists(caminho_iso) else nome_base
            if filtro in nome_base.lower():
                jogos_filtrados.append(jogo)
                listbox.insert(tk.END, nome_exibido)

    filtro_online_var.trace_add('write', lambda *args: exibir_jogos_filtrados())

    def atualizar_capa(event):
        index = listbox.curselection()
        if index:
            nome_lista = listbox.get(index)
            nome_limpo = nome_lista.replace(" (baixado)", "")
            for jogo in jogos_filtrados:
                if jogo["nome"] == nome_limpo:
                    capa = obter_capa(jogo["nome"])
                    if capa:
                        capa_label.config(image=capa, text='')
                        capa_label.image = capa
                    else:
                        capa_label.config(image='', text='Capa não encontrada')
                    break

    listbox.bind("<<ListboxSelect>>", atualizar_capa)

    def baixar_selecionado():
        index = listbox.curselection()
        if index:
            nome_lista = listbox.get(index)
            nome_limpo = nome_lista.replace(" (baixado)", "")
            for i, jogo in enumerate(jogos_filtrados):
                if jogo["nome"] == nome_limpo:
                    iniciar_download(jogo, listbox, index[0])
                    break
        else:
            messagebox.showwarning("Aviso", "Selecione um jogo para baixar.")

    tk.Button(aba_biblioteca, text="Baixar Jogo Selecionado", command=baixar_selecionado, font=('Arial', 12)).pack(pady=10)
    exibir_jogos_filtrados()

    # ==== ABA 2: Jogos Baixados ====
    aba_baixados = tk.Frame(notebook)
    notebook.add(aba_baixados, text="Jogos Baixados")

    tk.Label(aba_baixados, text="Jogos Baixados:", font=('Arial', 14)).pack(pady=5)
    filtro_baixado_var = tk.StringVar()
    tk.Entry(aba_baixados, textvariable=filtro_baixado_var, font=('Arial', 12)).pack(pady=5, fill='x', padx=10)

    lista_baixados = tk.Listbox(aba_baixados, font=('Arial', 12), width=60)
    lista_baixados.pack(pady=10)

    def exibir_baixados_filtrados():
        filtro = filtro_baixado_var.get().lower()
        formatos_dados = (".iso", ".bin", ".img", ".mdf", ".nrg", ".gz", ".chd", ".cso")
        arquivos = os.listdir(PASTA_JOGOS)

        exibidos = set()
        lista_baixados.delete(0, tk.END)

        for arquivo in sorted(arquivos):
            nome_arquivo = arquivo.lower()
            nome_base, ext = os.path.splitext(nome_arquivo)

            if ext in (".cue", ".mds", ".ccd"):
                continue  # pula arquivos auxiliares

            if ext in formatos_dados and filtro in nome_arquivo:
                if nome_base not in exibidos:
                    exibidos.add(nome_base)
                    lista_baixados.insert(tk.END, arquivo)



    filtro_baixado_var.trace_add('write', lambda *args: exibir_baixados_filtrados())

    tk.Button(aba_baixados, text="Abrir Pasta de Downloads", command=utils.abrir_pasta, font=('Arial', 12)).pack(pady=5)

    def atualizar_lista_baixados():
        exibir_baixados_filtrados()

    # Define a função de atualização dinamicamente no módulo utils
    utils.atualizar_lista_baixados = atualizar_lista_baixados

    atualizar_lista_baixados()
    root.mainloop()
