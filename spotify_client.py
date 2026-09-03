import requests

# URL base do seu mock server local FastAPI
BASE_URL = "http://127.0.0.1:8000"

def buscar_musica(q: str, limit: int = 10):
    """
    Busca músicas no dataset através do endpoint /v1/search do mock.
    """
    url = f"{BASE_URL}/v1/search"
    params = {"q": q, "type": "track"}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro na busca: {response.status_code} - {response.text}")

def obter_features_acusticas(track_id: int):
    """
    Retorna as características acústicas de uma música específica pelo ID (índice).
    """
    url = f"{BASE_URL}/v1/audio-features/{track_id}"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao buscar características: {response.status_code} - {response.text}")

def obter_recomendacoes(seed_index: int, limit: int = 5):
    """
    Envia o índice de uma música de referência e recebe as recomendações baseadas em cosseno.
    """
    url = f"{BASE_URL}/v1/recommendations"
    params = {"seed_index": seed_index, "limit": limit}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao buscar recomendações: {response.status_code} - {response.text}")