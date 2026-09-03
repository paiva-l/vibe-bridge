from spotify_client import buscar_musica, obter_recomendacoes

print("--- 1. Testando a busca de músicas ---")
busca = buscar_musica(q="a", limit=3)
tracks = busca.get("tracks", {}).get("items", [])

if not tracks:
    print("Nenhuma música encontrada na busca. Verifique se o dataset_clean.csv tem dados.")
else:
    primeira_musica = tracks[0]
    seed_id = int(primeira_musica["id"])
    print(f"Música semente escolhida: '{primeira_musica['name']}' (ID/Índice: {seed_id})")

    print("\n--- 2. Testando o motor de recomendação por cosseno ---")
    recomendacoes = obter_recomendacoes(seed_index=seed_id, limit=3)

    print(f"Baseado em: {recomendacoes['seed_track']['name']}")
    print("Recomendações acústicas geradas:")
    for rec in recomendacoes["tracks"]:
        print(f" - {rec['name']} por {rec['artists'][0]['name']} (Similaridade: {rec['similarity_score']:.4f})")