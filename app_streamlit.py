import streamlit as st
from spotify_client import buscar_musica, obter_recomendacoes

# Configuração da página
st.set_page_config(page_title="Vibe Bridge - Recomendador Spotify", page_icon="🎵", layout="centered")

st.title("🎵 Vibe Bridge: Motor de Recomendação Acústica")
st.markdown("Encontre músicas semelhantes com base nas características acústicas e abra direto no Spotify!")

# Inicializa o histórico de feedback no session_state se não existir
if 'feedback_generos' not in st.session_state:
    st.session_state['feedback_generos'] = []

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
                track_id = t['id']
                rotulo = f"{nome_musica} - {artista}"
                opcoes_tracks[rotulo] = track_id
            
            # Seleção da música semente pelo usuário
            musica_escolhida_rotulo = st.selectbox("Selecione a música de referência (Seed):", list(opcoes_tracks.keys()))
            seed_id = opcoes_tracks[musica_escolhida_rotulo]
            
            if st.button("Gerar Recomendações Acústicas 🚀", type="primary"):
                # Limpa o feedback anterior ao gerar uma nova seed
                st.session_state['feedback_generos'] = []
                # Passa o feedback acumulado para refinar a busca se houver
                st.session_state['recs_data'] = obter_recomendacoes(
                    seed_track_id=seed_id, 
                    limit=limite_recs, 
                    feedback_context=st.session_state['feedback_generos']
                )
            
            # Renderiza as recomendações se existirem no estado da sessão
            if 'recs_data' in st.session_state and st.session_state['recs_data']:
                recs = st.session_state['recs_data']
                
                st.markdown("---")
                st.subheader(f"✨ Recomendações baseadas em: **{recs['seed_track']['name']}**")
                
                # Exibe a música seed com link do Spotify
                seed_spotify_url = recs['seed_track']['external_urls']['spotify']
                st.markdown(f"🔗 [Ouvir música de referência no Spotify]({seed_spotify_url})")
                
                st.markdown("### 🎧 Top Recomendações:")
                
                # Exibe cada música recomendada com botões de feedback
                for i, rec in enumerate(recs["tracks"], 1):
                    nome = rec['name']
                    artista = rec['artists'][0]['name']
                    score = rec['similarity_score']
                    url_spotify = rec['external_urls']['spotify']
                    preview_url = rec.get('preview_url')
                    track_key = rec.get('id', str(i))
                    
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{i}. {nome}** — *{artista}*")
                            st.caption(f"Grau de Afinidade Acústica: **{score:.2f}**")
                            
                            if preview_url:
                                st.audio(preview_url, format="audio/mp3")
                            else:
                                st.caption("🔇 Prévia de 30s indisponível no momento para esta faixa.")
                                
                        with col2:
                            st.markdown(f"[▶ Abrir no Spotify]({url_spotify})")
                        
                        # Linha de botões de Feedback de Afinidade (Curtir / Descurtir)
                        c_like, c_dislike, c_empty = st.columns([1, 1, 4])
                        
                        # Chaves únicas para os botões baseadas no índice e ID da track
                        if c_like.button("👍 Curtir", key=f"like_{i}_{track_key}"):
                            if artista not in st.session_state['feedback_generos']:
                                st.session_state['feedback_generos'].append(artista)
                                st.success(f"Feedback registrado! O estilo de '{artista}' será valorizado.")
                                # Atualiza as recomendações instantaneamente com base no feedback
                                st.session_state['recs_data'] = obter_recomendacoes(
                                    seed_track_id=seed_id, 
                                    limit=limite_recs, 
                                    feedback_context=st.session_state['feedback_generos']
                                )
                                st.rerun()
                                
                        if c_dislike.button("👎 Descurtir", key=f"dislike_{i}_{track_key}"):
                            st.warning(f"Entendido! Evitando faixas semelhantes a '{artista}'.")
                            # Recarrega removendo ou filtrando
                            st.rerun()

                        st.divider()
                        
    except Exception as e:
        st.error(f"Erro ao comunicar com a API do Spotify. Verifique suas credenciais nos Secrets do Streamlit.\n\nDetalhes: {e}")

else:
    if 'recs_data' in st.session_state:
        del st.session_state['recs_data']
    st.info("💡 Digite o nome de uma música ou artista acima para começar a buscar.")