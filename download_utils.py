import requests
import time

def download_com_progresso(url, destino, update_callback=None):
    resposta = requests.get(url, stream=True)
    total = int(resposta.headers.get('content-length', 0))
    baixado = 0
    inicio = time.time()

    with open(destino, 'wb') as f:
        for bloco in resposta.iter_content(chunk_size=1024 * 1024):  # 1 MB
            if bloco:
                f.write(bloco)
                baixado += len(bloco)
                if update_callback:
                    perc = int(100 * baixado / total)
                    velocidade = baixado / (time.time() - inicio + 0.01)  # em B/s
                    restante = total - baixado
                    update_callback(perc, velocidade, baixado, total)
