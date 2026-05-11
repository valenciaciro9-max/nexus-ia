import streamlit as st
import requests
import os
from datetime import datetime, timedelta
import pyttsx3

API_KEY = os.getenv("API_KEY")

# 🎤 VOZ (masculina)
engine = pyttsx3.init()
engine.setProperty('rate', 170)

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

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

if st.session_state.chat_actual not in st.session_state.historial:
    st.session_state.historial[st.session_state.chat_actual] = []

# ======================
# ⏳ LÍMITE 24H SIMULADO
# ======================
if "limite_activo" not in st.session_state:
    st.session_state.limite_activo = False

if "limite_time" not in st.session_state:
    st.session_state.limite_time = None

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

if st.sidebar.button("📞 Llamada con voz"):
    st.session_state.modo = "Llamada"
    st.success("📞 Modo llamada activado")

# ======================
# 🧠 SYSTEM PROMPT
# ======================
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Eres NexusIA, una inteligencia artificial. "

        "CAPACIDADES: "
        "- Programación (Roblox, Lua, Python) "
        "- Explicar temas generales "
        "- Resolver matemáticas y lógica "

        "ESTILO: "
        "- Claro, natural y directo "
        "- No inventes información "

        "REGLAS: "
        "- No hacking ni cosas ilegales "
        "- Usa solo funciones reales de Roblox si se pide código "
        "- Si algo no existe, explica alternativa "

        "- Si el modo es 'Llamada', responde corto, natural y como conversación en vivo "
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

    # 🔊 VOZ EN MODO LLAMADA
    if st.session_state.modo == "Llamada":
        engine.say(reply)
        engine.runAndWait()

    return reply

# ======================
# 💬 CHAT
# ======================
historial = st.session_state.historial[st.session_state.chat_actual]

for msg in historial:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ======================
# ✍️ INPUT
# ======================
entrada = st.chat_input("Escribe algo...")

if entrada:

    if not check_limit():
        st.error("⛔ Alcanzaste tu límite. Vuelve en 24 horas.")
        st.stop()

    respuesta = preguntar_ia(entrada)

    st.chat_message("user").write(entrada)
    st.chat_message("assistant").write(respuesta)

# ======================
# ⚠️ FOOTER
# ======================
st.markdown(
    "<hr>"
    "<p style='text-align:center; font-size:12px; color:gray;'>"
    "NexusIA puede cometer errores. Comprueba la información importante."
    "</p>",
    unsafe_allow_html=True
)