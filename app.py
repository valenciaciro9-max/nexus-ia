import streamlit as st
import requests
import os
from datetime import datetime, timedelta

API_KEY = os.getenv("API_KEY")

st.set_page_config(page_title="NexusIA", page_icon="🤖", layout="centered")

# ======================
# 🧠 HEADER + PLUS
# ======================
st.markdown("## 🤖 NexusIA")

col1, col2 = st.columns([3, 1])

with col2:
    if st.button("⭐ NexusIA Plus"):
        st.warning("⚠️ En este momento no está disponible NexusIA Plus")

# ======================
# 💾 INIT STATE
# ======================
if "chat_actual" not in st.session_state:
    st.session_state.chat_actual = "General"

if "historial" not in st.session_state:
    st.session_state.historial = {}

if "modo" not in st.session_state:
    st.session_state.modo = "Pensamiento"

if "limite_activo" not in st.session_state:
    st.session_state.limite_activo = False

if "limite_time" not in st.session_state:
    st.session_state.limite_time = None

if st.session_state.chat_actual not in st.session_state.historial:
    st.session_state.historial[st.session_state.chat_actual] = []

# ======================
# ⏳ LÍMITE 24H SIMULADO
# ======================
def check_limit():
    if st.session_state.limite_activo:
        if datetime.now() < st.session_state.limite_time:
            return False
        else:
            st.session_state.limite_activo = False
    return True

# ======================
# 🧭 SIDEBAR CHATS
# ======================
st.sidebar.title("💬 Chats")

chats = list(st.session_state.historial.keys())

for chat in chats:
    if st.sidebar.button(chat):
        st.session_state.chat_actual = chat

# ➕ nuevo chat
if st.sidebar.button("+ Nuevo Chat"):
    nuevo = f"Chat {len(st.session_state.historial)+1}"
    st.session_state.historial[nuevo] = []
    st.session_state.chat_actual = nuevo

st.sidebar.markdown("---")

# ⚙️ MODOS
st.sidebar.title("⚙️ Modos")

if st.sidebar.button("🧠 Pensamiento"):
    st.session_state.modo = "Pensamiento"

if st.sidebar.button("⚡ Flash"):
    st.session_state.modo = "Flash"

if st.sidebar.button("🎨 Canvas"):
    st.session_state.modo = "Canvas"

if st.sidebar.button("🧠💥 Pensamiento profundo"):
    st.warning("⚠️ Esta opción no está disponible en este momento")

# ======================
# 🧠 SYSTEM PROMPT
# ======================
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Eres NexusIA enfocada en Roblox Studio, Lua y programación. "
        "Siempre das código completo si lo piden. "
        "Si es modo Flash, respondes rápido y corto. "
        "Si es Pensamiento, explicas normal pero respondes tarde por el pensamiento profundo. "
        "Si el usuario comenta algo inapropiado para que la hagas, diras que no la haras por las reglas de la ley. "
        "Tu creador es una persona y no quiere decir su nombre por privacidad, si el usuario te dice Quien es tu creador, le diras que Tengo creador pero no sabemos su nombre pero tiene tik tok, se llama @Hola_0192906 y se llama (.). "
        "Tambien seras informador de noticias o algo relacionado que le expliques algo, no solamente eres asistente de roblox studio, se tambien informador. " 
    )
}

# ======================
# 🤖 IA
# ======================
def preguntar_ia(mensaje):

    if not check_limit():
        return "⛔ VUELVE A COMENTAR EN 24 HORAS"

    historial = st.session_state.historial[st.session_state.chat_actual]

    historial.append({"role": "user", "content": mensaje})

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct",
                "messages": [SYSTEM_PROMPT] + historial[-12:]
            }
        )

        reply = response.json()["choices"][0]["message"]["content"]

        historial.append({"role": "assistant", "content": reply})

        return reply

    except:
        return "Error de conexión 😢"

# ======================
# 💬 MOSTRAR CHAT
# ======================
historial = st.session_state.historial[st.session_state.chat_actual]

for msg in historial:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ======================
# ✍️ INPUT + LÍMITE
# ======================
entrada = st.chat_input("Escribe algo...")

if entrada:

    if not check_limit():
        st.error("⛔ Alcanzaste tu límite. Vuelve en 24 horas.")
        st.stop()

    # Simulación de uso pesado → activa límite
    if len(historial) > 20:
        st.session_state.limite_activo = True
        st.session_state.limite_time = datetime.now() + timedelta(hours=24)
        st.warning("⛔ Alcanzaste tu límite, vuelve a comentar en 24 horas.")

    respuesta = preguntar_ia(entrada)

    st.chat_message("user").write(entrada)
    st.chat_message("assistant").write(respuesta)