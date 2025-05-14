import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import os
import threading

import utils
from downloader import baixar_e_descompactar, PASTA_JOGOS
from igdb_api import baixar_capa
from remover import deletar_jogo

CAPAS_DIR = "capas"
FORMATOS_VALIDOS = (".iso", ".bin", ".img", ".mdf", ".nrg", ".gz", ".chd", ".cso")

downloads_em_andamento = {}

def carregar_jogos():
    with open('jogos.json', 'r') as f:
        return json.load(f)

def obter_capa(nome_jogo):
    try:
        caminho = os.path.join(CAPAS_DIR, f"{nome_jogo}.jpg")
        if not os.path.exists(caminho):
            baixar_capa(nome_jogo)
        imagem = Image.open(caminho).resize((250, 410), Image.LANCZOS)
        return ImageTk.PhotoImage(imagem)
    except:
        return None

def jogo_baixado(nome_base):
    for root, _, arquivos in os.walk(PASTA_JOGOS):
        for arquivo in arquivos:
            if arquivo.lower().endswith(FORMATOS_VALIDOS) and nome_base.lower() in arquivo.lower():
                return True
    return False

def atualizar_info_botao(jogo):
    selecao = listbox.curselection()
    if jogo_baixado(jogo["nome"]):
        botao_acao.config(text="Baixado", state="disabled")
        botao_excluir.config(text="Excluir Jogo", state="normal", command=lambda j=jogo: excluir_jogo_confirmacao(j))
        botao_excluir.pack(pady=5)
    else:
        if selecao:
            i = selecao[0]
            botao_acao.config(text="Baixar Jogo", state="normal", command=lambda j=jogo, i=i: iniciar_download(j, listbox, i))
        else:
            botao_acao.config(text="Baixar Jogo", state="disabled")
        botao_excluir.pack_forget()

def excluir_jogo_confirmacao(jogo):
    if messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir '{jogo['nome']}'?"):
        arquivos = deletar_jogo(jogo["nome"])
        if arquivos:
            messagebox.showinfo("Sucesso", f"{len(arquivos)} arquivos removidos.")
        else:
            messagebox.showwarning("Aviso", "Nenhum arquivo encontrado para remover.")
        exibir_jogos_filtrados()
        botao_acao.config(text="", state="disabled")
        botao_excluir.pack_forget()
        capa_label.config(image='', text='')

def iniciar_download(jogo, listbox, index):
    progresso_var = tk.StringVar(value=f"{jogo['nome']} (Iniciando...)")
    listbox.delete(index)
    listbox.insert(index, progresso_var.get())
    botao_acao.config(text="Baixando...", state="disabled")
    botao_excluir.pack_forget()

    def update_status(texto):
        progresso_var.set(texto)
        listbox.delete(index)
        listbox.insert(index, progresso_var.get())
        downloads_em_andamento[jogo['nome']] = texto

    def thread_func():
        baixar_e_descompactar(jogo, update_status)
        downloads_em_andamento.pop(jogo['nome'], None)
        exibir_jogos_filtrados()
        atualizar_info_botao(jogo)

    threading.Thread(target=thread_func).start()

def abrir_janela_downloads():
    janela = tk.Toplevel()
    janela.title("Downloads em Andamento")
    janela.geometry("500x300")

    frame = tk.Frame(janela)
    frame.pack(fill='both', expand=True, padx=10, pady=10)

    texto_status = tk.Text(frame, state='disabled', wrap='word')
    texto_status.pack(fill='both', expand=True)

    def atualizar_texto():
        texto_status.config(state='normal')
        texto_status.delete("1.0", tk.END)
        for nome, status in downloads_em_andamento.items():
            texto_status.insert(tk.END, f"{nome}: {status}\n")
        texto_status.config(state='disabled')
        janela.after(1000, atualizar_texto)

    atualizar_texto()

def criar_interface():
    global exibir_jogos_filtrados, botao_acao, botao_excluir, listbox, capa_label

    root = tk.Tk()
    root.title("PSLoad")
    largura, altura = 1100, 700
    x = (root.winfo_screenwidth() - largura) // 2
    y = (root.winfo_screenheight() - altura) // 2
    root.geometry(f"{largura}x{altura}+{x}+{y}")
    root.resizable(False, False)

    aba_biblioteca = tk.Frame(root)
    aba_biblioteca.pack(expand=True, fill='both')

    tk.Label(aba_biblioteca, text="Jogos Disponíveis:", font=('Arial', 14)).pack(pady=5)
    filtro_online_var = tk.StringVar()
    tk.Entry(aba_biblioteca, textvariable=filtro_online_var, font=('Arial', 12)).pack(pady=5, fill='x', padx=10)

    conteudo_frame = tk.Frame(aba_biblioteca)
    conteudo_frame.pack(expand=True, fill='both')

    sidebar_frame = tk.Frame(conteudo_frame, width=10)
    sidebar_frame.pack(side="left", fill="y", padx=10)
    tk.Label(sidebar_frame, text="Jogos Baixados", font=('Arial', 12, 'bold')).pack(pady=5)

    listbox = tk.Listbox(conteudo_frame, font=('Arial', 12), width=30)
    listbox.pack(side="left", fill="both", expand=True, padx=10)
    scrollbar = tk.Scrollbar(conteudo_frame)
    scrollbar.pack(side="left", fill="y")
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    lateral_frame = tk.Frame(conteudo_frame)
    lateral_frame.pack(side="left", padx=10, pady=10)

    capa_label = tk.Label(lateral_frame)
    capa_label.pack()
    botao_acao = tk.Button(lateral_frame, text="", font=('Arial', 12))
    botao_acao.pack(pady=10)
    botao_excluir = tk.Button(lateral_frame, text="Excluir Jogo", font=('Arial', 12))



    canvas_sidebar = tk.Canvas(sidebar_frame, width=200)
    scrollbar_sidebar = tk.Scrollbar(sidebar_frame, orient="vertical", command=canvas_sidebar.yview)
    scrollable_frame = tk.Frame(canvas_sidebar)

    scrollable_frame.bind("<Configure>", lambda e: canvas_sidebar.configure(scrollregion=canvas_sidebar.bbox("all")))
    canvas_sidebar.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas_sidebar.configure(yscrollcommand=scrollbar_sidebar.set)
    canvas_sidebar.pack(side="top", fill="both", expand=True)
    scrollbar_sidebar.pack(side="right", fill="y")

    miniaturas = {}
    jogos = carregar_jogos()
    jogos_filtrados = list(jogos)

    def selecionar_jogo(nome_jogo):
        for i, jogo in enumerate(jogos_filtrados):
            if jogo["nome"] == nome_jogo:
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(i)
                listbox.see(i)
                listbox.event_generate("<<ListboxSelect>>")
                break

    def atualizar_sidebar_baixados():
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        miniaturas.clear()

        for jogo in jogos:
            if jogo_baixado(jogo["nome"]):
                try:
                    caminho = os.path.join(CAPAS_DIR, f"{jogo['nome']}.jpg")
                    if os.path.exists(caminho):
                        imagem = Image.open(caminho).resize((40, 60), Image.LANCZOS)
                        imagem_tk = ImageTk.PhotoImage(imagem)
                        miniaturas[jogo["nome"]] = imagem_tk

                        item_frame = tk.Frame(scrollable_frame)
                        item_frame.pack(pady=5, anchor='w', fill='x')

                        lbl_imagem = tk.Label(item_frame, image=imagem_tk)
                        lbl_imagem.pack(side='left', padx=5)

                        lbl_texto = tk.Label(item_frame, text=jogo["nome"], font=('Arial', 8), anchor='w', wraplength=120, justify='left')
                        lbl_texto.pack(side='left', padx=5)

                        # Evento para ambos abrirem o jogo
                        lbl_imagem.bind("<Button-1>", lambda e, nome=jogo["nome"]: selecionar_jogo(nome))
                        lbl_texto.bind("<Button-1>", lambda e, nome=jogo["nome"]: selecionar_jogo(nome))

                except:
                    continue


    def exibir_jogos_filtrados():
        filtro = filtro_online_var.get().lower()
        listbox.delete(0, tk.END)
        jogos_filtrados.clear()
        for jogo in jogos:
            nome_base = jogo["nome"]
            if filtro in nome_base.lower():
                jogos_filtrados.append(jogo)
                nome_exibido = f"{nome_base} (baixado)" if jogo_baixado(nome_base) else nome_base
                listbox.insert(tk.END, nome_exibido)
        atualizar_sidebar_baixados()

    filtro_online_var.trace_add('write', lambda *args: exibir_jogos_filtrados())

    def atualizar_capa(event):
        index = listbox.curselection()
        if index:
            nome_lista = listbox.get(index[0])
            nome_limpo = nome_lista.replace(" (baixado)", "")
            for jogo in jogos_filtrados:
                if jogo["nome"] == nome_limpo:
                    capa = obter_capa(jogo["nome"])
                    if capa:
                        capa_label.config(image=capa, text='')
                        capa_label.image = capa
                    else:
                        capa_label.config(image='', text='Capa não encontrada')
                    atualizar_info_botao(jogo)
                    break

    listbox.bind("<<ListboxSelect>>", atualizar_capa)
    botao_ver_downloads = tk.Button(sidebar_frame, text="Ver Downloads", font=('Arial', 12), command=abrir_janela_downloads)
    botao_ver_downloads.pack(pady=10)
    exibir_jogos_filtrados()
    root.mainloop()