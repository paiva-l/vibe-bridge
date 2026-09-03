import streamlit as st
from spotify_client import buscar_musica, obter_recomendacoes

# Configuração da página
st.set_page_config(page_title="Vibe Bridge - Recomendador Spotify", page_icon="🎵", layout="centered")

st.title("🎵 Vibe Bridge: Motor de Recomendação Acústica")
st.markdown("Encontre músicas semelhantes com base nas características acústicas e abra direto no Spotify!")

# Barra lateral para navegação / opções
st.sidebar.header("Configurações")
limite_recs = st.sidebar.slider("Quantidade de Recomendações", min_value=1, max_value=10, value=5)

# Campo de busca de músicas
termo_busca = st.text_input("Busque por uma música ou artista no Spotify:", placeholder="Ex: Unholy, Taylor Swift, Lo-Fi...")

if termo_busca:
    try:
        # Chama a API real do Spotify
        resultado = buscar_musica(q=termo_busca, limit=10)
        tracks = resultado.get("tracks", {}).get("items", [])
        
        if not tracks:
            st.warning("Nenhuma música encontrada com esse termo.")
        else:
            st.success(f"Encontradas {len(tracks)} músicas correspondentes:")
            
            # Cria um dicionário para o selectbox mostrar o nome e o artista
            opcoes_tracks = {}
            for t in tracks:
                nome_musica = t['name']
                artista = t['artists'][0]['name']
                track_id = t['id'] # ID alfanumérico real do Spotify
                rotulo = f"{nome_musica} - {artista}"
                opcoes_tracks[rotulo] = track_id
            
            # Seleção da música semente pelo usuário
            musica_escolhida_rotulo = st.selectbox("Selecione a música de referência (Seed):", list(opcoes_tracks.keys()))
            seed_id = opcoes_tracks[musica_escolhida_rotulo]
            
            if st.button("Gerar Recomendações Acústicas 🚀", type="primary"):
                with st.spinner("Consultando a API do Spotify e calculando recomendações..."):
                    recs = obter_recomendacoes(seed_track_id=seed_id, limit=limite_recs)
                
                st.markdown("---")
                st.subheader(f"✨ Recomendações baseadas em: **{recs['seed_track']['name']}**")
                
                # Exibe a música seed com link do Spotify
                seed_spotify_url = recs['seed_track']['external_urls']['spotify']
                st.markdown(f"🔗 [Ouvir música de referência no Spotify]({seed_spotify_url})")
                
                st.markdown("### 🎧 Top Recomendações:")
                
                # Exibe cada música recomendada
                for i, rec in enumerate(recs["tracks"], 1):
                    nome = rec['name']
                    artista = rec['artists'][0]['name']
                    score = rec['similarity_score']
                    url_spotify = rec['external_urls']['spotify']
                    
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{i}. {nome}** — *{artista}*")
                            st.caption(f"Grau de Afinidade Acústica: **{score:.2f}**")
                        with col2:
                            st.markdown(f"[▶ Abrir no Spotify]({url_spotify})")
                        st.divider()
                        
    except Exception as e:
        st.error(f"Erro ao comunicar com a API do Spotify. Verifique suas credenciais nos Secrets do Streamlit.\n\nDetalhes: {e}")

else:
    st.info("💡 Digite o nome de uma música ou artista acima para começar a buscar.")