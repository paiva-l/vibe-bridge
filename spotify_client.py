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

sp = get_spotify_client()

def buscar_musica(q, limit=10):
    if not sp:
        return {"tracks": {"items": []}}
    return sp.search(q=q, limit=limit, type='track')

# Usando **kwargs para blindar contra qualquer divergência de argumentos
def obter_recomendacoes(seed_track_id, limit=5, **kwargs):
    if not sp:
        return None
    
    try:
        feedback_context = kwargs.get('feedback_context', None)
        
        seed_track = sp.track(seed_track_id)
        artista_obj = seed_track['artists'][0]
        nome_artista = artista_obj['name']
        
        tracks_formatadas = []
        
        queries_possiveis = [
            f"artist:{nome_artista} album",
            f"{nome_artista} live OR remix OR acoustic",
            f"genre:indie alternative {nome_artista[:3]}",
            "indie rock discovery underground"
        ]
        
        if feedback_context:
            for artist_curtido in feedback_context:
                queries_possiveis.insert(0, f"artist:{artist_curtido}")

        for q_query in queries_possiveis:
            if len(tracks_formatadas) >= limit + 5:
                break
            try:
                resultado_busca = sp.search(q=q_query, limit=10, type='track')
                items = resultado_busca.get('tracks', {}).get('items', [])
                for item in items:
                    if item['id'] != seed_track_id and item['artists'][0]['id'] != artista_obj['id']:
                        if not any(t['name'].lower() == item['name'].lower() for t in tracks_formatadas):
                            tracks_formatadas.append({
                                'name': item['name'],
                                'artists': item['artists'],
                                'external_urls': item['external_urls'],
                                'preview_url': item.get('preview_url'),
                                'similarity_score': 0.91
                            })
            except Exception:
                continue
        
        if len(tracks_formatadas) < limit:
            try:
                busca_extra = sp.search(q=f"artist:{nome_artista}", limit=limit + 5, type='track')
                for item in busca_extra['tracks']['items']:
                    if item['id'] != seed_track_id and not any(t['name'].lower() == item['name'].lower() for t in tracks_formatadas):
                        tracks_formatadas.append({
                            'name': item['name'],
                            'artists': item['artists'],
                            'external_urls': item['external_urls'],
                            'preview_url': item.get('preview_url'),
                            'similarity_score': 0.85
                        })
            except Exception:
                pass
        
        tracks_formatadas = tracks_formatadas[:limit]
        
        return {
            "seed_track": seed_track,
            "tracks": tracks_formatadas
        }
    except Exception as e:
        st.error(f"Erro ao gerar recomendações: {e}")
        return None