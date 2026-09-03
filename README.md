# 🎵 Vibe Bridge — O Tradutor de Vibes para o Spotify

> **Sistema de Recomendação Musical por Interpolação Vetorial, Similaridade Acústica e Descoberta de Artistas Independentes**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FAISS](https://img.shields.io/badge/FAISS-Meta%20AI-orange.svg)](https://github.com/facebookresearch/faiss)
[![Spotify API](https://img.shields.io/badge/API-Spotify%20Web%20API-1DB954.svg)](https://developer.spotify.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Sobre o Projeto

O **Vibe Bridge** é um módulo de recomendação e transição musical inteligente projetado para eliminar quebras bruscas de ritmo em sessões de escuta e promover a descoberta orgânica de artistas independentes. 

Utilizando um espaço multidimensional de atributos de áudio (*audio features*) e busca por vizinhos mais próximos de alta performance (**FAISS**), o sistema constrói uma "ponte sonora" gradativa entre duas faixas de referência escolhidas pelo usuário (**Ponto A $\rightarrow$ Ponto B**).

---

## 🎯 Problema & Solução

### O Problema
* **Transições Abruptas:** Recomendações convencionais frequentemente alternam entre faixas de energias incompatíveis, aumentando a taxa de rejeição (*skips*).
* **Bolha de Popularidade:** Algoritmos focados em engajamento global tendem a favorecer artistas altamente populares (*head of the tail*), invisibilizando produções independentes.

### A Solução (Vibe Bridge)
* **Interpolação Vetorial ($\alpha$):** Criação de um vetor alvo intermediário que varia suavemente entre a música de origem e a de destino.
* **Descoberta Guiada:** Injeção controlada de faixas de baixa popularidade ($Popularity < 40$) ao longo da trajetória, garantindo compatibilidade acústica sem perda de fluidez.

---

## ⚡ Arquitetura da Solução
