# test_minimal.py
import streamlit as st

st.set_page_config(page_title="Test Minimal", layout="wide")

st.title("🧪 Test Minimal")
st.write("Ce test vérifie si Streamlit fonctionne correctement.")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Bonjour ! Comment puis-je vous aider ?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Votre message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"Vous avez dit: {user_input}. Voici une réponse test."
    })
    st.rerun()
