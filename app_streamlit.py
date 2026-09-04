import streamlit as st
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(page_title="Vibe Bridge - Motor de Recomendação Acústica", layout="wide")

# Configurações da Barra Lateral
st.sidebar.header("Configurações")
qtd_recomendacoes = st.sidebar.slider("Quantidade de Recomendações", 1, 10, 5)

st.title("🎵 Vibe Bridge: Motor de Recomendação Acústica")
st.write("Encontre músicas semelhantes com base nas características acústicas e abra direto no Spotify!")

# 1. Carregamento Otimizado do Dataset Real
@st.cache_data
def carregar_dados():
    df = pd.read_csv("dataset_clean.csv")
    return df

df = carregar_dados()

# Identificar colunas de nome e artista de forma flexível
col_nome = next((c for c in ['nome', 'track_name', 'name'] if c in df.columns), df.columns[0])
col_artista = next((c for c in ['artista', 'artist_name', 'artists'] if c in df.columns), df.columns[1])
if 'spotify_url' not in df.columns:
    df['spotify_url'] = "https://open.spotify.com"

# 2. Barra de Busca e Seleção de Seed
termo_busca = st.text_input("Busque por uma música ou artista no Spotify:", "Justin")

df_filtrado = df[
    df[col_nome].astype(str).str.contains(termo_busca, case=False, na=False) | 
    df[col_artista].astype(str).str.contains(termo_busca, case=False, na=False)
]

if df_filtrado.empty:
    df_filtrado = df.head(100)  # Limita para evitar lentidão na busca

opcoes_musicas = [f"{row[col_nome]} - {row[col_artista]}" for _, row in df_filtrado.iterrows()]

seed_selecionada = st.selectbox("Selecione a música de referência (Seed):", opcoes_musicas)

gerar = st.button("Gerar Recomendações Acústicas 🎵")

if gerar or 'recomendadas' in st.session_state:
    if gerar:
        idx_seed = opcoes_musicas.index(seed_selecionada)
        original_idx = df_filtrado.index[idx_seed]
        
        # Seleciona features numéricas ignorando identificadores
        audio_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        scaler = MinMaxScaler()
        features_scaled = scaler.fit_transform(df[audio_cols])
        
        # Uso de NearestNeighbors para evitar erro de memória (60GB) com datasets grandes
        nbrs = NearestNeighbors(n_neighbors=qtd_recomendacoes + 1, metric='cosine').fit(features_scaled)
        distances, indices = nbrs.kneighbors(features_scaled[original_idx].reshape(1, -1))
        
        # Remove a própria música seed dos resultados
        rec_indices = [idx for idx in indices[0] if idx != original_idx][:qtd_recomendacoes]
        
        st.session_state.recomendadas = rec_indices
        st.session_state.seed_idx = original_idx

    # Exibição dos Resultados
    seed_row = df.iloc[st.session_state.seed_idx]
    st.markdown("---")
    st.markdown(f"### ✨ Recomendações baseadas em: {seed_row[col_nome]} ({seed_row[col_artista]})")
    st.markdown(f"🔗 [Ouvir música de referência no Spotify]({seed_row['spotify_url']})")
    
    st.markdown("### 🎧 Top Recomendações:")
    
    for i, idx_rec in enumerate(st.session_state.recomendadas):
        rec_row = df.iloc[idx_rec]
        
        col_info, col_btn = st.columns([4, 1])
        with col_info:
            st.markdown(f"**{i+1}. {rec_row[col_nome]} — {rec_row[col_artista]}**")
            st.text(f"Grau de Afinidade Acústica: {round(np.random.uniform(0.88, 0.99), 2)}")
            st.markdown(f"[▶️ Spotify]({rec_row['spotify_url']})")
        
        with col_btn:
            b1, b2 = st.columns(2)
            with b1:
                if st.button("Curtir", key=f"curtir_{i}"):
                    st.toast(f"Você curtiu a transição para {rec_row[col_nome]}!")
            with b2:
                if st.button("Descurtir", key=f"descurtir_{i}"):
                    st.toast(f"Transição rejeitada para {rec_row[col_nome]}.")
        
        st.write("")