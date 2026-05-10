import streamlit as st
import requests
import os

# 🔐 API KEY desde Streamlit Secrets
API_KEY = os.getenv("API_KEY")

st.set_page_config(page_title="NexusIA", page_icon="🤖", layout="centered")

st.title("🤖 NexusIA")
st.caption("Bienvenido a la IA, Disfruta. 🌐")

# 💾 historial
if "historial" not in st.session_state:
    st.session_state.historial = []

# 🧠 personalidad mejorada
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Eres NexusIA, una inteligencia artificial tipo ChatGPT. "
        "Ayudas con programación (especialmente Roblox Studio, Lua y scripts). "
        "Si el usuario pide código, siempre lo das completo y funcional. "
        "Si pide arreglar un script, lo corriges y explicas brevemente el error. "
        "Usa bloques de código ``` cuando sea necesario. "
        "Sé claro, útil y directo."
        "Si el usuario pide informacion que no este relacionado con roblox studio, lo dices. "
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


# 💬 UI estilo chat + copiar código
for msg in st.session_state.historial:
    with st.chat_message(msg["role"]):

        contenido = msg["content"]
        st.markdown(contenido)

        # 📋 botón copiar si hay código
        if "```" in contenido:
            if st.button("📋 Copiar código", key=contenido[:20]):
                codigo = contenido.split("```")[1]
                st.code(codigo)
                st.success("Código listo para copiar 👍")

# ✍️ input
entrada = st.chat_input("Escribe algo...")

if entrada:
    respuesta = preguntar_ia(entrada)
    st.chat_message("user").write(entrada)
    st.chat_message("assistant").write(respuesta)