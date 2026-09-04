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
        nome_seed = seed_track['name']
        artista_obj = seed_track['artists'][0]
        nome_artista = artista_obj['name']
        
        tracks_formatadas = []
        
        # Cria buscas altamente dinâmicas baseadas no nome da música e do artista escolhido
        queries_possiveis = [
            f"{nome_artista} {nome_seed}",
            f"artist:{nome_artista} electronic OR rock OR pop",
            f"track:{nome_seed}",
            f"artist:{nome_artista} discovery"
        ]
        
        # Executa as buscas para povoar as recomendações de forma variada
        for q_query in queries_possiveis:
            if len(tracks_formatadas) >= limit + 5:
                break
            try:
                resultado_busca = sp.search(q=q_query, limit=10, type='track')
                items = resultado_busca.get('tracks', {}).get('items', [])
                for item in items:
                    # Evita duplicar a música seed, o mesmo artista principal ou músicas repetidas na lista
                    if item['id'] != seed_track_id and item['artists'][0]['id'] != artista_obj['id']:
                        if not any(t['name'] == item['name'] for t in tracks_formatadas):
                            tracks_formatadas.append({
                                'name': item['name'],
                                'artists': item['artists'],
                                'external_urls': item['external_urls'],
                                'preview_url': item.get('preview_url'),
                                'similarity_score': 0.91
                            })
            except Exception:
                continue
        
        # Se a busca dinâmica trouxer poucos itens, faz um fallback complementar focado no artista
        if len(tracks_formatadas) < limit:
            try:
                busca_extra = sp.search(q=f"artist:{nome_artista}", limit=limit + 5, type='track')
                for item in busca_extra['tracks']['items']:
                    if item['id'] != seed_track_id and not any(t['name'] == item['name'] for t in tracks_formatadas):
                        tracks_formatadas.append({
                            'name': item['name'],
                            'artists': item['artists'],
                            'external_urls': item['external_urls'],
                            'preview_url': item.get('preview_url'),
                            'similarity_score': 0.85
                        })
            except Exception:
                pass
        
        # Limita à quantidade exata solicitada
        tracks_formatadas = tracks_formatadas[:limit]
        
        return {
            "seed_track": seed_track,
            "tracks": tracks_formatadas
        }
    except Exception as e:
        st.error(f"Erro ao gerar recomendações independentes: {e}")
        return None