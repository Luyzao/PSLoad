import requests
import os

TWITCH_CLIENT_ID = 'ksmayqr1g71ytaf1q7dc2gtjcp36zq'
TWITCH_CLIENT_SECRET = '8sariu8xgj1ab3mr7na3z56wqguz12'
IGDB_TOKEN = None
CAPAS_DIR = "capas"
os.makedirs(CAPAS_DIR, exist_ok=True)

def obter_token_igdb():
    global IGDB_TOKEN
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        IGDB_TOKEN = response.json()["access_token"]
    else:
        raise Exception("Erro ao obter token da Twitch IGDB")

def baixar_capa(nome):
    global IGDB_TOKEN
    if not IGDB_TOKEN:
        obter_token_igdb()

    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {IGDB_TOKEN}"
    }
    query = f'search "{nome}"; fields name,cover.image_id;'

    response = requests.post(url, data=query, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data and "cover" in data[0]:
            image_id = data[0]["cover"]["image_id"]
            image_url = f"https://images.igdb.com/igdb/image/upload/t_cover_big/{image_id}.jpg"
            img_data = requests.get(image_url).content
            with open(os.path.join(CAPAS_DIR, f"{nome}.jpg"), 'wb') as f:
                f.write(img_data)
    else:
        print(f"Erro na IGDB: {response.status_code} - {response.text}")
