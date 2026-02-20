import streamlit as st
import logging
from core.qualification import QUESTIONS

# Configuration du logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("matching_chat")

st.title("🤖 Chat Matching")

# Initialisation des états 
if "messages" not in st.session_state:
    st.session_state.messages = []

if "qualification" not in st.session_state:
    st.session_state.qualification = {}

if "current_step" not in st.session_state:
    st.session_state.current_step = 0

if "phase" not in st.session_state:
    st.session_state.phase = "qualification"

# Initialisation du premier message
if len(st.session_state.messages) == 0 and st.session_state.phase == "qualification":
    try:
        first_question = st.session_state.pipeline.start_qualification_sync()
        st.session_state.messages.append({
            "role": "assistant",
            "content": first_question
        })
    except Exception as e:
        logger.error(f"Erreur d'initialisation: {str(e)}")
        st.error("Erreur d'initialisation. Veuillez rafraîchir la page.")

# Affichage des messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Logique principale
user_input = st.chat_input("Votre réponse...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    # Phase de qualification
    if st.session_state.phase == "qualification":
        try:
            current_key = QUESTIONS[st.session_state.current_step][0]
            st.session_state.qualification[current_key] = user_input

            next_question = st.session_state.pipeline.get_next_qualification_question(
                QUESTIONS,
                st.session_state.current_step
            )

            if next_question:
                st.session_state.current_step += 1
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": next_question
                })
            else:
                # Dernière question - passage à la reformulation
                st.session_state.qualification[QUESTIONS[st.session_state.current_step][0]] = user_input
                qualification_text = "\n".join(
                    f"{k}: {v}" for k, v in st.session_state.qualification.items()
                )
                reform_response = st.session_state.pipeline.reformulate_sync(qualification_text)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reform_response
                })
                st.session_state.phase = "chat"

        except Exception as e:
            logger.error(f"Erreur dans la phase de qualification: {str(e)}")
            st.error("Une erreur est survenue. Veuillez réessayer.")

    # Phase de chat
    elif st.session_state.phase == "chat":
        qualification_text = "\n".join(
            f"{k}: {v}" for k, v in st.session_state.qualification.items()
        )

        # ⭐ Version ultra-simple comme votre exemple
        answer = st.session_state.pipeline.generate_sync(
            question=user_input,
            context=[qualification_text],
            conversation=st.session_state.messages
        )

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })
    st.rerun()