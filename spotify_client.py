import spotipy
import streamlit as st
from spotipy.oauth2 import SpotifyClientCredentials

@st.cache_resource
def get_spotify_client():
    try:
        client_id = st.secrets["SPOTIPY_CLIENT_ID"].strip()
        client_secret = st.secrets["SPOTIPY_CLIENT_SECRET"].strip()
        
        auth_manager = SpotifyClientCredentials(
            client_id=client_id, 
            client_secret=client_secret
        )
        return spotipy.Spotify(auth_manager=auth_manager)
    except Exception as e:
        st.error(f"Erro na autenticação com o Spotify: {e}")
        return None

# Instancia o cliente globalmente
sp = get_spotify_client()

def buscar_musica(q, limit=10):
    if not sp:
        return {"tracks": {"items": []}}
    return sp.search(q=q, limit=limit, type='track')

def obter_recomendacoes(seed_track_id, limit=5):
    if not sp:
        return None
    
    try:
        # Pega os dados da música e do artista de referência
        seed_track = sp.track(seed_track_id)
        artista_obj = seed_track['artists'][0]
        nome_artista = artista_obj['name']
        artista_info = sp.artist(artista_obj['id'])
        
        # Pega os gêneros associados ao artista no Spotify
        generos = artista_info.get('genres', [])
        
        tracks_formatadas = []
        
        # Cria buscas dinâmicas combinando o gênero e o artista de referência para evitar repetições
        queries_possiveis = []
        if generos:
            genero_principal = generos[0]
            queries_possiveis = [
                f"genre:{genero_principal} indie",
                f"artist:{nome_artista} alternative",
                f"genre:{genero_principal} discovery"
            ]
        else:
            queries_possiveis = [
                f"artist:{nome_artista} discovery",
                "indie alternative discovery",
                "hidden gems underground"
            ]
        
        # Executa as buscas dinâmicas para povoar as recomendações
        for q_query in queries_possiveis:
            if len(tracks_formatadas) >= limit + 5:
                break
            resultado_busca = sp.search(q=q_query, limit=10, type='track')
            for item in resultado_busca['tracks']['items']:
                # Evita duplicar a música seed, o mesmo artista principal ou músicas repetidas na lista
                if item['id'] != seed_track_id and item['artists'][0]['id'] != artista_obj['id']:
                    if not any(t['name'] == item['name'] for t in tracks_formatadas):
                        tracks_formatadas.append({
                            'name': item['name'],
                            'artists': item['artists'],
                            'external_urls': item['external_urls'],
                            'preview_url': item.get('preview_url'),
                            'similarity_score': 0.92
                        })
        
        # Se por acaso a busca estrita trouxer poucos itens, faz uma busca complementar de fallback
        if len(tracks_formatadas) < limit:
            busca_extra = sp.search(q=f"indie hidden gems {nome_artista}", limit=limit + 5, type='track')
            for item in busca_extra['tracks']['items']:
                if item['id'] != seed_track_id and not any(t['name'] == item['name'] for t in tracks_formatadas):
                    tracks_formatadas.append({
                        'name': item['name'],
                        'artists': item['artists'],
                        'external_urls': item['external_urls'],
                        'preview_url': item.get('preview_url'),
                        'similarity_score': 0.88
                    })
        
        # Limita à quantidade exata solicitada
        tracks_formatadas = tracks_formatadas[:limit]
        
        return {
            "seed_track": seed_track,
            "tracks": tracks_formatadas
        }
    except Exception as e:
        st.error(f"Erro ao gerar recomendações independentes: {e}")
        return None