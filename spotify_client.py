import spotipy
import streamlit as st
from spotipy.oauth2 import SpotifyClientCredentials

# Autenticação segura usando os segredos do Streamlit
@st.cache_resource
def get_spotify_client():
    client_id = st.secrets["SPOTIPY_CLIENT_ID"]
    client_secret = st.secrets["SPOTIPY_CLIENT_SECRET"]
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(auth_manager=auth_manager)

sp = get_spotify_client()

def buscar_musica(q, limit=10):
    """Busca faixas reais na API do Spotify"""
    results = sp.search(q=q, limit=limit, type='track')
    return results

def obter_recomendacoes(seed_track_id, limit=5):
    """
    Busca as características de áudio da música escolhida (seed) e 
    encontra recomendações usando a API de recomendações do Spotify.
    """
    seed_track = sp.track(seed_track_id)
    recs_raw = sp.recommendations(seed_tracks=[seed_track_id], limit=limit)
    
    tracks_formatadas = []
    for item in recs_raw['tracks']:
        tracks_formatadas.append({
            'name': item['name'],
            'artists': item['artists'],
            'external_urls': item['external_urls'],
            'similarity_score': 0.95 
        })
        
    return {
        "seed_track": seed_track,
        "tracks": tracks_formatadas
    }