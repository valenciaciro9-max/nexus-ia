import streamlit as st
import requests
import os

# 🔐 API KEY SEGURA (se carga desde Streamlit Secrets)
API_KEY = os.getenv("API_KEY")

st.set_page_config(page_title="NexusIA", page_icon="🤖", layout="centered")

st.title("🤖 NexusIA")
st.caption("IA tipo ChatGPT para PC y celular 🌐")

# 💾 historial del chat
if "historial" not in st.session_state:
    st.session_state.historial = []

# 🧠 personalidad de la IA
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Eres una inteligencia artificial tipo ChatGPT. "
        "Respondes de forma natural, clara y útil. "
        "No inventas información. Si no sabes algo, lo dices."
    )
}

# 🤖 función IA
def preguntar_ia(mensaje):
    st.session_state.historial.append({"role": "user", "content": mensaje})

    mensajes = [SYSTEM_PROMPT] + st.session_state.historial[-12:]

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct",
                "messages": mensajes
            }
        )

        if response.status_code != 200:
            return "Error conectando con la IA 😢"

        data = response.json()
        reply = data["choices"][0]["message"]["content"]

        st.session_state.historial.append({"role": "assistant", "content": reply})

        return reply

    except:
        return "Error de conexión 😢"


# 💬 mostrar historial
for msg in st.session_state.historial:
    st.chat_message(msg["role"]).write(msg["content"])


# ✍️ input tipo ChatGPT
entrada = st.chat_input("Escribe algo...")

if entrada:
    st.chat_message("user").write(entrada)
    respuesta = preguntar_ia(entrada)
    st.chat_message("assistant").write(respuesta)