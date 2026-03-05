import streamlit as st
from pathlib import Path

st.set_page_config(page_title="OK KÉVIN", page_icon="📡", layout="centered")

with open(Path(__file__).parent / "style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("<h1> OK KÉVIN</h1><p class='sub'>Votre correspondant mondial </p>", unsafe_allow_html=True)
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander(f" {len(msg['sources'])} source(s)"):
                for s in msg["sources"]:
                    st.caption(f"**{s['title']}** · {s['region']} · {s['date']} · [{s['url']}]({s['url']})")

if prompt := st.chat_input("Alors Kévin, quoi de neuf ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
   