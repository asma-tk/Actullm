import streamlit as st
import requests

st.set_page_config(page_title="Ok Kévin", page_icon="📰", layout="wide")

# ── Chargement du CSS externe ──────────────────────────────────
with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Config APIs ────────────────────────────────────────────────
# FRONT → api_front (8002) → C3 (8004) → ChromaDB (8003) → LLM (8005)
API_FRONT = "http://localhost:8002/ask"
API_LLM   = "http://localhost:8005/generate"

MODELS = ["mistral", "llama3", "ChatGPT"]  # Liste des modèles disponibles dans Ollam

# ── Session state ──────────────────────────────────────────────
if "model"          not in st.session_state: st.session_state.model          = "mistral"
if "rag_messages"   not in st.session_state: st.session_state.rag_messages   = []
if "norag_messages" not in st.session_state: st.session_state.norag_messages = []


# ── API calls ──────────────────────────────────────────────────
def ask_with_rag(question: str, model: str):
    """
    Avec RAG :
    FRONT → api_front (8002) → C3 (8004) → ChromaDB (8003) ↓ build_prompt ↓ LLM (8005)
    """
    try:
        r = requests.post(
            API_FRONT,
            json={"question": question, "mode": "rag", "model": model},
            timeout=120,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("answer", "—"), data.get("sources", [])
    except requests.exceptions.ConnectionError:
        return "❌ api_front (8002) non joignable.", []
    except requests.exceptions.Timeout:
        return "⏱️ Timeout — le LLM prend trop de temps.", []
    except Exception as e:
        return f"❌ Erreur : {e}", []


def ask_without_rag(question: str, model: str):
    """
    Sans RAG :
    Prompt direct → LLM (8005) — aucun contexte documentaire
    """
    prompt = (
        "Tu es un assistant journaliste. "
        "Réponds en français à la question suivante "
        "sans contexte documentaire supplémentaire.\n\n"
        f"Question : {question}\nRéponse :"
    )
    try:
        r = requests.post(
            API_LLM,
            json={"model": model, "prompt": prompt},
            timeout=120,
        )
        r.raise_for_status()
        return r.json().get("response", "—")
    except requests.exceptions.ConnectionError:
        return "❌ LLM Gateway (8005) non joignable."
    except requests.exceptions.Timeout:
        return "⏱️ Timeout — le LLM prend trop de temps."
    except Exception as e:
        return f"❌ Erreur : {e}"


# ── Header ─────────────────────────────────────────────────────
st.markdown('<h1 class="masthead">Ok Kévin, quoi de neuf ?</h1>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Discuter des dernières actualités · RAG · France 24</p>', unsafe_allow_html=True)

# ── Sélecteur de modèle (partagé, au-dessus des 2 chats) ──────
st.markdown(f"""
<div class="model-bar">
  <span class="model-lbl">Modèle actif</span>
  <span class="model-name">⬡ {st.session_state.model}</span>
</div>
""", unsafe_allow_html=True)

cols_btn = st.columns(len(MODELS))
for i, m in enumerate(MODELS):
    with cols_btn[i]:
        label = f"✦ {m}" if m == st.session_state.model else m
        if st.button(label, key=f"btn_{m}", use_container_width=True):
            st.session_state.model = m
            st.rerun()

st.markdown("<hr style='border:1px solid #1e1e1e; margin:1rem 0 1.5rem'>", unsafe_allow_html=True)

# ── Deux colonnes ──────────────────────────────────────────────
col_rag, col_norag = st.columns(2)

# ── Colonne gauche : AVEC RAG ──────────────────────────────────
with col_rag:
    st.markdown('<span class="col-badge badge-rag">⚡ Avec RAG</span>', unsafe_allow_html=True)

    # Zone scrollable des messages
    chat_rag = st.container(height=500)
    with chat_rag:
        for msg in st.session_state.rag_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander(f" {len(msg['sources'])} source(s)"):
                        for s in msg["sources"]:
                            st.caption(f"**{s.get('title','')}** · {s.get('region','')} · {s.get('date','')} · {s.get('url','')}")

    # Input collé en bas
    if prompt := st.chat_input("Kévin, quoi de neuf dans le monde ?", key="input_rag"):
        st.session_state.rag_messages.append({"role": "user", "content": prompt})
        with chat_rag:
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner(f"Recherche dans ChromaDB + {st.session_state.model}…"):
                    answer, sources = ask_with_rag(prompt, st.session_state.model)
                st.markdown(answer)
                if sources:
                    with st.expander(f" {len(sources)} source(s)"):
                        for s in sources:
                            st.caption(f"**{s.get('title','')}** · {s.get('region','')} · {s.get('date','')} · {s.get('url','')}")
        st.session_state.rag_messages.append({"role": "assistant", "content": answer, "sources": sources})

# ── Colonne droite : SANS RAG ──────────────────────────────────
with col_norag:
    st.markdown('<span class="col-badge badge-norag">○ Sans RAG</span>', unsafe_allow_html=True)

    # Zone scrollable des messages
    chat_norag = st.container(height=500)
    with chat_norag:
        for msg in st.session_state.norag_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Input collé en bas
    if prompt := st.chat_input("Kévin, quoi de neuf dans le monde ?", key="input_norag"):
        st.session_state.norag_messages.append({"role": "user", "content": prompt})
        with chat_norag:
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner(f"{st.session_state.model} répond sans contexte…"):
                    answer = ask_without_rag(prompt, st.session_state.model)
                st.markdown(answer)
        st.session_state.norag_messages.append({"role": "assistant", "content": answer})