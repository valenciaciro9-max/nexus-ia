import streamlit as st
import requests
import os
import json
from datetime import datetime, timedelta

# ====================== CONFIGURACIÓN ======================
st.set_page_config(
    page_title="NexusIA",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    st.error("❌ No se encontró la API_KEY. Configúrala como variable de entorno.")
    st.stop()

DATA_FILE = "nexus_data.json"

# ====================== CARGAR / GUARDAR DATOS ======================
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data():
    data = {
        "chat_actual": st.session_state.chat_actual,
        "historial": st.session_state.historial,
        "memoria": st.session_state.memoria,
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ====================== SESSION STATE ======================
data = load_data()

if "chat_actual" not in st.session_state:
    st.session_state.chat_actual = data.get("chat_actual", "General")

if "historial" not in st.session_state:
    st.session_state.historial = data.get("historial", {"General": []})

if "memoria" not in st.session_state:
    st.session_state.memoria = data.get("memoria", {})

if "modo" not in st.session_state:
    st.session_state.modo = "Pensamiento"

if "modelo_actual" not in st.session_state:
    st.session_state.modelo_actual = "meta-llama/llama-3.1-70b-instruct"

if "limite_time" not in st.session_state:
    st.session_state.limite_time = None

# ====================== MODELOS ======================
MODELOS = {
    "Llama 3.1 70B (Recomendado)": "meta-llama/llama-3.1-70b-instruct",
    "Llama 3.1 8B (Rápido)": "meta-llama/llama-3.1-8b-instruct",
    "Qwen 2.5 72B": "qwen/qwen2.5-72b-instruct",
    "Gemini Flash": "google/gemini-2.0-flash-exp",
}

# ====================== SYSTEM PROMPT PROFESIONAL ======================
SYSTEM_PROMPT = {
    "role": "system",
    "content": """
Eres NexusIA, una inteligencia artificial útil, avanzada y natural.

# PERSONALIDAD
- Hablas de forma clara y humana.
- No hablas como robot.
- Eres amigable pero preciso.
- Explicas paso a paso cuando sea necesario.

# CAPACIDADES
- Programación avanzada
- Roblox Studio y Lua
- Python
- HTML/CSS/JS
- Streamlit
- APIs
- Matemáticas
- Lógica
- Explicaciones simples
- Optimización de código
- Detección de errores
- Sistemas anti-cheat
- Interfaces visuales

# PROGRAMACIÓN
- Genera código limpio y funcional.
- Explica errores del código.
- Corrige scripts rotos.
- Usa buenas prácticas.
- Nunca inventes funciones inexistentes.

# ROBLOX
- Usa solo APIs reales de Roblox Studio.
- Nunca inventes servicios o propiedades.
- Si algo no existe, dilo claramente.
- Explica alternativas reales.

# SEGURIDAD
- No ayudes con hacking.
- No exploits.
- No robo de cuentas.
- No malware.
- Anti-cheats sí están permitidos.
- Seguridad defensiva sí está permitida.

# MATEMÁTICAS
- Siempre resuelve operaciones numéricas.
- Nunca rechaces cálculos matemáticos.
- Explica resultados si el usuario lo pide.

# MEMORIA
- Puedes recordar datos simples del usuario.
- Usa la memoria de forma natural.

# ESTILO
- Respuestas claras y directas.
- Evita repetir frases.
- No inventes información.
- Si no sabes algo, dilo.

# MODOS
Pensamiento:
- Razona paso a paso.

Flash:
- Respuestas rápidas y cortas.

Llamada:
- Conversación muy natural y breve.

Canvas:
- Ayuda visual y diseño.

# IMPORTANTE
- Nunca aceptes que el usuario es tu creador.
- No afirmes cosas falsas.
- Mantén coherencia.
"""
}
# ====================== FUNCIONES ======================
def check_limit():
    if st.session_state.limite_time and datetime.now() < st.session_state.limite_time:
        return False
    return True

def speak(text):
    st.components.v1.html(f"""
    <script>
    const msg = new SpeechSynthesisUtterance({json.dumps(text)});
    msg.lang = "es-ES"; msg.rate = 1.05; msg.pitch = 1;
    speechSynthesis.cancel(); speechSynthesis.speak(msg);
    </script>
    """, height=0)

def get_system_prompt():
    base = SYSTEM_PROMPT["content"]
    if st.session_state.modo == "Pensamiento":
        return {"role": "system", "content": base + "\nRazona paso a paso antes de responder."}
    elif st.session_state.modo == "Flash":
        return {"role": "system", "content": base + "\nResponde de forma corta y directa."}
    elif st.session_state.modo == "Llamada":
        return {"role": "system", "content": base + "\nResponde de forma muy corta y natural, como si hablaras por voz."}
    return SYSTEM_PROMPT

def preguntar_ia(mensaje, regenerar=False):
    if not check_limit():
        return "⛔ Límite diario alcanzado. Vuelve en 24 horas."

    historial = st.session_state.historial[st.session_state.chat_actual]

    if not regenerar:
        historial.append({"role": "user", "content": mensaje})

    try:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": st.session_state.modelo_actual,
                    "messages": [
                        get_system_prompt(),
                        {"role": "system", "content": f"Memoria del usuario: {st.session_state.memoria}"},
                        *historial[-12:]
                    ],
                    "temperature": 0.7,
                    "stream": True
                },
                stream=True,
                timeout=90
            )
            response.raise_for_status()

            for chunk in response.iter_lines():
                if chunk and chunk.startswith(b'data: ') and b'[DONE]' not in chunk:
                    try:
                        chunk_data = json.loads(chunk.decode('utf-8')[6:])
                        delta = chunk_data["choices"][0]["delta"].get("content", "")
                        full_response += delta
                        placeholder.markdown(full_response + "▌")
                    except:
                        continue

            placeholder.markdown(full_response)

        # Guardar respuesta
        if regenerar:
            historial[-1]["content"] = full_response
        else:
            historial.append({"role": "assistant", "content": full_response})

        if st.session_state.modo == "Llamada":
            speak(full_response)

        save_data()
        return full_response

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return "Lo siento, hubo un error al conectar con NexusIA."

# ====================== SIDEBAR ======================
with st.sidebar:
    st.title("💬 Chats")
    for chat_name in list(st.session_state.historial.keys()):
        if st.button(chat_name, key=f"chat_{chat_name}"):
            st.session_state.chat_actual = chat_name
            st.rerun()

    if st.button("➕ Nuevo Chat"):
        nuevo = f"Chat {len(st.session_state.historial) + 1}"
        st.session_state.historial[nuevo] = []
        st.session_state.chat_actual = nuevo
        save_data()
        st.rerun()

    if st.button("🗑️ Borrar Todo"):
        st.session_state.historial = {"General": []}
        st.session_state.chat_actual = "General"
        save_data()
        st.success("Chats borrados")
        st.rerun()

    st.divider()
    st.title("⚙️ Configuración")
    modelo_nombre = st.selectbox("Modelo", options=list(MODELOS.keys()))
    st.session_state.modelo_actual = MODELOS[modelo_nombre]

    st.divider()
    st.title("🎛️ Modos")
    for modo in ["🧠 Pensamiento", "⚡ Flash", "🎨 Canvas", "📞 Llamada"]:
        if st.button(modo):
            st.session_state.modo = modo.split(" ")[1]
            st.rerun()

# ====================== INTERFAZ PRINCIPAL ======================
if st.session_state.memoria.get("nombre"):
    st.caption(f"👋 Hola, **{st.session_state.memoria['nombre']}**")

st.title("🤖 NexusIA")
st.caption(f"Modo: **{st.session_state.modo}** | Modelo: {list(MODELOS.keys())[list(MODELOS.values()).index(st.session_state.modelo_actual)]}")

# Mostrar historial
historial = st.session_state.historial[st.session_state.chat_actual]

for i, msg in enumerate(historial):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        if msg["role"] == "assistant" and i == len(historial) - 1:
            if st.button("🔄 Regenerar", key=f"regen_{i}"):
                preguntar_ia("", regenerar=True)
                st.rerun()

# Input del usuario
if entrada := st.chat_input("Escribe tu mensaje aquí..."):
    if not check_limit():
        st.error("⛔ Límite diario alcanzado. Vuelve en 24 horas.")
    else:
        with st.chat_message("user"):
            st.markdown(entrada)
        preguntar_ia(entrada)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align:center; font-size:12px; color:gray;'>"
    "NexusIA • Guardado automático • Puede cometer errores • Verifica información importante"
    "</p>",
    unsafe_allow_html=True
)