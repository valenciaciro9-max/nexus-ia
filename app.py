import streamlit as st
import requests
import os

API_KEY = os.getenv("API_KEY")

st.set_page_config(page_title="NexusIA", page_icon="🤖", layout="centered")

st.title("🤖 NexusIA")
st.caption("Bienvenido a la IA, Disfruta 🌐")

# 💬 CHATS DISPONIBLES
chats = ["General", "Texto Rainbow en Lua"]

# 🧠 chat actual
if "chat_actual" not in st.session_state:
    st.session_state.chat_actual = "General"

# 💾 historial por chat
if "historial" not in st.session_state:
    st.session_state.historial = {}

if st.session_state.chat_actual not in st.session_state.historial:
    st.session_state.historial[st.session_state.chat_actual] = []

# 🧭 SIDEBAR (lista de chats)
st.sidebar.title("💬 Chats")

for chat in chats:
    if st.sidebar.button(chat):
        st.session_state.chat_actual = chat

st.sidebar.markdown("---")

# ⭐ NEXUSIA PLUS BLOQUEADO
if st.sidebar.button("⭐ NexusIA Plus"):
    st.warning("⚠️ En este momento no está disponible NexusIA Plus")

# 🧠 SYSTEM PROMPT
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Eres NexusIA, una IA tipo ChatGPT enfocada en programación Roblox Studio y Lua. "
        "Si piden código, lo das completo y funcional. "
        "Si piden arreglar algo, corriges y explicas brevemente. "
        "Usa bloques de código cuando sea necesario. "
        "Si el tema no es programación, responde brevemente que estás enfocada en Roblox Studio."
        "Recuerda que no tienes sentimiento, el unico sentimiento que tienes es Felicidad y con emojis para sentir bien. "
        "Si piden algo inapropiado o algo similar, le diras que no podras decir eso. "
    )
}

# 🤖 IA
def preguntar_ia(mensaje):
    historial = st.session_state.historial[st.session_state.chat_actual]

    historial.append({"role": "user", "content": mensaje})

    mensajes = [SYSTEM_PROMPT] + historial[-12:]

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

        reply = response.json()["choices"][0]["message"]["content"]

        historial.append({"role": "assistant", "content": reply})

        return reply

    except:
        return "Error de conexión 😢"

# 💬 MOSTRAR CHAT ACTUAL
historial = st.session_state.historial[st.session_state.chat_actual]

for msg in historial:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # 📋 copiar código
        if "```" in msg["content"]:
            if st.button("📋 Copiar código", key=msg["content"][:20]):
                codigo = msg["content"].split("```")[1]
                st.code(codigo)
                st.success("Código copiado 👍")

# ✍️ INPUT
entrada = st.chat_input("Escribe algo...")

if entrada:
    respuesta = preguntar_ia(entrada)
    st.chat_message("user").write(entrada)
    st.chat_message("assistant").write(respuesta)