import streamlit as st
import time, random

st.set_page_config(page_title="Ok Kévin", page_icon="📰", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [data-testid="stApp"], .main, .block-container {
    background: #ffffff !important;
}
#MainMenu, footer, [data-testid="stHeader"] { display: none !important; }
.block-container { max-width: 800px !important; padding: 2rem !important; }

[data-testid="stChatMessage"] {
    background: #f8f9fa !important;
    border: 1px solid #e9ecef !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
}
[data-testid="stChatMessage"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: .82rem !important;
    line-height: 1.75 !important;
}


</style>
""", unsafe_allow_html=True)

# ── Mock data ──────────────────────────────────────────────────
ARTICLES = [
    {"region": "europe",       "title": "Sommet UE : accord sur la migration",      "date": "02 mars 2026", "content": "Les 27 s'accordent sur la répartition des migrants après deux jours de négociations à Bruxelles."},
    {"region": "afrique",      "title": "Sénégal : participation record 72%",        "date": "02 mars 2026", "content": "Les Sénégalais se rendent aux urnes en masse pour les législatives."},
    {"region": "moyen_orient", "title": "Cessez-le-feu : nouvelle session à Doha",  "date": "01 mars 2026", "content": "Médiation américaine et qatarie pour tenter de mettre fin aux hostilités."},
    {"region": "asie",         "title": "Japon : plan de relance 50 milliards",     "date": "01 mars 2026", "content": "Tokyo annonce un plan massif pour soutenir l'économie nationale."},
    {"region": "ameriques",    "title": "Brésil : tensions sur la réforme fiscale", "date": "28 fév. 2026", "content": "Le Parlement est divisé sur la réforme fiscale du gouvernement Lula."},
]
KEYS = {
    "europe":       ["europe", "france", "ue"],
    "afrique":      ["afrique", "sénégal", "mali"],
    "moyen_orient": ["moyen-orient", "doha", "israël"],
    "asie":         ["asie", "japon", "chine"],
    "ameriques":    ["brésil", "amérique", "lula"],
}

def ask_kevin(question):
    # 👉 Remplacer par LangChain + ChromaDB + Mistral quand prêt
    time.sleep(0.8)
    q = question.lower()
    top3 = sorted(ARTICLES,
        key=lambda a: random.uniform(.5,.65) + (.3 if any(k in q for k in KEYS[a["region"]]) else 0),
        reverse=True)[:3]
    answer = "\n\n".join(f"**{a['title']}** ({a['region']}, {a['date']}) : {a['content']}" for a in top3)
    answer += "\n\n> *Mode démo — connecte Ollama + ChromaDB pour le vrai RAG*"
    sources = [{"title": a["title"], "region": a["region"], "date": a["date"]} for a in top3]
    return answer, sources

# ── UI ─────────────────────────────────────────────────────────
st.title("📰 Ok Kévin, quoi de neuf ?")
st.caption("posez votre question")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander(f"📎 {len(msg['sources'])} source(s)"):
                for s in msg["sources"]:
                    st.caption(f"**{s['title']}** · {s['region']} · {s['date']}")

if prompt := st.chat_input("Alors Kévin, quoi de neuf ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Kévin consulte ses sources..."):
            answer, sources = ask_kevin(prompt)
        st.markdown(answer)
        with st.expander(f"📎 {len(sources)} source(s)"):
            for s in sources:
                st.caption(f"**{s['title']}** · {s['region']} · {s['date']}")

    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})