import streamlit as st
import requests

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

def ask_kevin(question):
    response = requests.post(
        "http://localhost:8002/ask",
        json={"question": question}
    )
    data = response.json()
    return data["answer"], data["sources"]

# ── UI ────────────────────────────────────────────────────────
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