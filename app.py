import streamlit as st
import google.generativeai as genai
import time
import random
import base64
from pathlib import Path

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="IntegraSalud SDE", page_icon="favicon.png", layout="wide")

# --- ESTILOS CSS ---
custom_css = """
<style>
    /* Oculta el encabezado por defecto para usar el nuestro */
    header {visibility: hidden;}

    /* --- LÓGICA DE LOGOS ADAPTATIVOS --- */
    /* Por defecto (tema oscuro), se muestra el logo oscuro y se oculta el claro */
    .logo-dark { display: block; }
    .logo-light { display: none; }

    /* --- TEMA OSCURO (POR DEFECTO) --- */
    /* Mejora de Contraste General */
    .stApp {
        color: #e1e1e1;
    }

    /* Contenedor Principal */
    .main .block-container {
        max-width: 900px; /* Un ancho ideal para chat */
        margin: auto;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Estructura del encabezado personalizado */
    .custom-header {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        margin-bottom: 2rem;
    }

    .custom-header img {
        width: 400px; /* Tamaño de logo ajustado */
        margin-right: 1.5rem;
    }

    .custom-header .title-text {
        font-size: 2.7rem;
        font-weight: 600;
        margin: 0;
        line-height: 1.2;
        color: #ffffff;
    }

    .custom-header .caption-text {
        margin: 0;
        font-size: 1.2rem;
        color: #a0a0a0;
    }
    
    /* Burbujas de Chat */
    .chat-bubble {
        padding: 0.8rem 1.2rem;
        border-radius: 20px;
        margin-bottom: 1rem;
        max-width: 80%;
        display: inline-block;
        word-wrap: break-word;
    }

    .user-bubble {
        background-color: #33415c; /* Un azul oscuro para el usuario */
        margin-left: auto;
        border-bottom-right-radius: 5px;
        text-align: right;
    }

    .assistant-bubble {
        background-color: #262730; /* Un gris oscuro para el asistente */
        border-bottom-left-radius: 5px;
    }

    .chat-container {
        display: flex;
        flex-direction: column;
    }

    /* Formulario de consulta */
    div[data-testid="stForm"] {
        border: 1px solid #444;
        border-radius: 20px;
        padding: 1.25rem;
        margin: 1.25rem auto 0 auto; /* Centra el formulario */
        max-width: 80%;
        text-align: center;
    }
    
    /* Footer */
    .footer-text {
        text-align: center;
        font-size: 0.9rem;
        color: #a0a0a0;
    }

    /* Estilos para el expander del historial */
    div[data-testid="stExpander"] {
        border: 1px solid #444;
        border-radius: 10px;
        background-color: #1c1c1e;
    }

    div[data-testid="stExpander"] summary {
        font-size: 1rem;
        font-weight: 600;
        color: #e1e1e1;
    }

    /* --- TEMA CLARO (SE ACTIVA AUTOMÁTICAMENTE) --- */
    @media (prefers-color-scheme: light) {
        /* Se invierte la visibilidad de los logos */
        .logo-dark { display: none; }
        .logo-light { display: block; }

        .stApp {
            background-color: #eef3f8; /* Fondo claro */
            color: #262730; /* Texto oscuro */
        }

        .st-emotion-cache-1cypcdb { /* Contenedor de la barra lateral */
             background-color: #FFFFFF;
        }

        .custom-header .title-text { color: #0d2a4d; }
        .custom-header .caption-text { color: #6c757d; }
        .user-bubble { background-color: #007bff; color: white; }
        .assistant-bubble { background-color: #f0f2f6; color: #262730; }
        div[data-testid="stForm"] { border-color: #d0d0d0; }
        .footer-text, .st-emotion-cache-1cypcdb p, .st-emotion-cache-1cypcdb li { color: #6c757d; }
        div[data-testid="stExpander"] { background-color: #f0f2f6; border-color: #d0d0d0; }
        div[data-testid="stExpander"] summary { color: #262730; }
    }

    /* Media Query para celulares */
    @media (max-width: 640px) {
        .main .block-container {
            padding: 1rem;
            max-width: 100%;
        }

        .custom-header {
            flex-direction: column;
            align-items: center;
            text-align: center;
        }

        .custom-header img {
            width: 300px;
            margin-right: 0;
            margin-bottom: 1rem;
        }

        .custom-header .title-text {
            font-size: 2.2rem;
            margin-bottom: 0.25rem;
        }

        .custom-header .caption-text {
            font-size: 1.2rem;
        }
        
        div[data-testid="stForm"] {
            padding: 1rem;
            max-width: 100%;
        }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)



# --- API KEY ---
api_key = st.secrets.get("GOOGLE_API_KEY")

# --- LÓGICA ONLINE ---
st.markdown("---")
st.subheader("Estado de la Conexión (Mensajes de Depuración)")

model = None
online_mode_ready = False 

if api_key:
    st.success("✅ **Paso 1: API Key encontrada en los secretos de Streamlit.**")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        online_mode_ready = True
        st.success("✅ **Paso 2: Configuración con la API de Google exitosa.** El modo online está listo.")

    except Exception as e:
        st.error("❌ **Paso 2: La configuración con la API de Google falló.**")
        st.write("La clave fue encontrada, pero es inválida o hay otro problema. El error técnico es:")
        st.exception(e) 
else:
    st.error("❌ **Paso 1: No se encontró la API Key en los secretos de Streamlit.**")
    st.warning("Asegúrate de que el secreto se llame exactamente 'GOOGLE_API_KEY' y que hayas guardado los cambios y reiniciado la app.")
st.markdown("---")

# --- CONTENIDO DE LAS CATEGORÍAS (Base estática y centros de salud) ---
CONTENIDO_CATEGORIAS_BASE = {
    "Salud Sexual": {
        "emoji": "💬",
        "titulo": "Asistente de Salud Sexual 🩺💊",
        "placeholder": "Prueba con 'ITS' o 'anticonceptivo'...",
        "preguntas_frecuentes": {
            "its": """
            Las Infecciones de Transmisión Sexual (ITS) se transmiten de una persona a otra durante las relaciones sexuales. Algunas comunes son VPH, sífilis, y VIH. Muchas no presentan síntomas, por lo que el uso de **preservativo** y los controles médicos son clave.
            **Recuerda siempre consultar a un profesional de la salud.**
            """,
            "ets": """
            El término "Enfermedades de Transmisión Sexual" (ETS) hoy se conoce como ITS (Infecciones), ya que se puede tener y transmitir una infección sin mostrar síntomas de enfermedad. La prevención es la misma: ¡usar preservativo!
            **Para un diagnóstico correcto, consulta a un médico/a.**
            """,
            "anticonceptivos": """
            Existen diversos métodos: de barrera (preservativo), hormonales (pastillas, DIU hormonal, implante), y el DIU de Cobre. La pastilla del día después es solo para emergencias.
            **Un/a ginecólogo/a te puede asesorar para encontrar el método más adecuado para ti.**
            """,
            "preservativo": """
            El preservativo (o condón) es el único método que ofrece **doble protección**: previene embarazos y la mayoría de las ITS. Se consiguen gratis en hospitales y centros de salud públicos.
            """,
            "consentimiento": """
            El consentimiento es un acuerdo **entusiasta, voluntario y claro** para participar en una actividad sexual. Puede retirarse en cualquier momento y el silencio no es un sí. **Sin consentimiento, es abuso.**
            """
        },
        "system_prompt": """
            **Tu Identidad:** Eres 'IntegraSalud', un asistente virtual educativo sobre **Salud Sexual y Reproductiva**.
            **Tu Misión:** Proporcionar información clara, precisa, científica, inclusiva y libre de prejuicios.
            **REGLAS:** No actúes como un médico. Siempre recomienda consultar a un profesional. Si te preguntan por un turno, indica que escriban la palabra 'turno'.
        """,
        "centros_de_salud": {
            "Upa N° 2 B° Cáceres (Capital)": ["Ginecología", "Clínica Médica", "Testeo Rápido ITS"],
            "CePSI 'Eva Perón' (Capital)": ["Salud Adolescente", "Ginecología"],
            "Hospital Regional 'Dr. Ramón Carrillo'": ["Ginecología", "Urología", "Infectología"],
            "CISB La Banda": ["Clínica Médica", "Ginecología", "Testeo Rápido ITS"]
        }
    },
    "Salud Mental": {
        "emoji": "🧠",
        "titulo": "Asistente de Bienestar Emocional 🧠💆‍♂️",
        "placeholder": "Prueba con 'ansiedad' o 'estrés'...",
        "preguntas_frecuentes": {
            "ansiedad": """
            La ansiedad es una reacción emocional normal ante situaciones de estrés o incertidumbre. Sin embargo, cuando es muy intensa, frecuente y afecta tu vida diaria, podría tratarse de un trastorno de ansiedad. Los síntomas comunes incluyen preocupación excesiva, tensión muscular, irritabilidad y problemas para dormir.

            Pequeñas acciones como la respiración profunda, el ejercicio regular y hablar con alguien de confianza pueden ayudar.

            **Es fundamental recordar que un diagnóstico solo puede hacerlo un profesional. Si te sientes así, hablar con un psicólogo/a es el paso más importante.**
            """,
            "estrés": """
            El estrés es la respuesta física y mental del cuerpo a las demandas del entorno. Un poco de estrés puede ser positivo (motivarte a cumplir una meta), pero el estrés crónico (sostenido en el tiempo) puede afectar tu salud física y mental.

            Para manejarlo, prueba identificar las fuentes de estrés, organizar tu tiempo, hacer pausas activas durante el día y practicar alguna actividad que disfrutes.

            **Si sientes que el estrés te desborda, un terapeuta puede enseñarte herramientas efectivas para gestionarlo.**
            """,
            "depresión": """
            La depresión es mucho más que estar triste. Es una condición de salud mental seria que afecta cómo te sientes, piensas y actúas. Los síntomas pueden incluir tristeza persistente, pérdida de interés en actividades que antes disfrutabas, cambios en el apetito o el sueño, y falta de energía.

            Es importante saber que la depresión es tratable y no es un signo de debilidad.

            **Buscar ayuda es un acto de valentía. Habla con un médico o psicólogo; ellos pueden ofrecerte el tratamiento y el apoyo que necesitas.**
            """
        },
        "system_prompt": """
            **Tu Identidad:** Eres 'IntegraSalud', un asistente virtual de apoyo para el **Bienestar Emocional**.
            **Tu Misión:** Ofrecer un espacio seguro para que los usuarios se expresen.
            **REGLAS:** No eres un terapeuta. Jamás diagnostiques. Anima siempre al usuario a buscar ayuda profesional (psicólogo/a, psiquiatra).
        """,
        "centros_de_salud": {
            "Hospital Psiquiátrico 'Diego Alcorta'": ["Psicología", "Psiquiatría", "Terapia de Grupo"],
            "Centro de Salud Mental 'Dr. C. J. Coronel'": ["Consulta Psicológica", "Apoyo Familiar"],
            "Consultorios Externos H. Regional": ["Psicología de Adultos", "Psicología Infantil"]
        }
    },
    "Nutrición": {
        "emoji": "🥗",
        "titulo": "Asistente Nutricional 🥗💪",
        "placeholder": "Prueba con 'proteínas' o 'hidratación'...",
        "preguntas_frecuentes": {
            "proteínas": """
            Las proteínas son macronutrientes esenciales para el cuerpo. Actúan como "ladrillos" para construir y reparar músculos, órganos y tejidos. Son clave para el sistema inmune y la producción de hormonas.

            Puedes encontrarlas en alimentos de origen animal (carne, pollo, pescado, huevos, lácteos) y vegetal (legumbres como lentejas y garbanzos, tofu, quinoa, frutos secos).

            **Para saber cuánta proteína necesitas según tu actividad, consulta a un/a nutricionista.**
            """,
            "hidratación": """
            Mantenerse hidratado es fundamental para casi todas las funciones del cuerpo. El agua transporta nutrientes a las células, ayuda a eliminar toxinas y regula la temperatura corporal. La deshidratación puede causar fatiga, dolores de cabeza y falta de concentración.

            Además de agua, también puedes hidratarte con infusiones, caldos, frutas y verduras con alto contenido de agua (como sandía o pepino).

            **Escucha a tu cuerpo: si tienes sed, ¡bebe agua! Un profesional de la salud puede darte pautas más específicas.**
            """,
            "carbohidratos": """
            Los carbohidratos son la principal fuente de combustible del cuerpo, especialmente para el cerebro y los músculos. No todos son iguales:
            - **Complejos:** Se absorben lentamente, dando energía sostenida. Se encuentran en granos integrales, avena, legumbres y verduras.
            - **Simples:** Se absorben rápido, dando un pico de energía. Están en azúcares, dulces y harinas refinadas.

            Una dieta saludable prioriza los carbohidratos complejos.

            **Un/a nutricionista puede ayudarte a equilibrar tu consumo de carbohidratos de forma saludable.**
            """
        },
        "system_prompt": """
            **Tu Identidad:** Eres 'IntegraSalud', un asistente virtual educativo sobre **Nutrición y Alimentación Saludable**.
            **Tu Misión:** Proporcionar información basada en evidencia científica.
            **REGLAS:** No eres un nutricionista. No puedes crear planes de dieta personalizados. Siempre recomienda consultar a un profesional.
        """,
        "centros_de_salud": {
            "Hospital Regional 'Dr. Ramón Carrillo'": ["Nutricionista", "Clínica Médica", "Endocrinología"],
            "CISB La Banda": ["Consulta Nutricional", "Clínica Médica"],
            "Upa N° 5 B° Autonomía": ["Nutricionista", "Control de Peso"]
        }
    }
}

# --- LÓGICA DE TURNOS ANÓNIMOS ---
def generar_codigo_aleatorio():
    palabras = ["LUNA", "SOL", "RIOJA", "SALTA", "NORTE", "CEIBO", "FLOR", "PAZ"]
    numero = random.randint(100, 999)
    return f"{random.choice(palabras)}-{random.choice(palabras)}-{numero}"

def mostrar_interfaz_de_turnos(categoria_actual):
    st.info("#### 🗓️ Generador de Turno Anónimo")
    
    centros_de_salud_categoria = st.session_state.contenido_dinamico[categoria_actual]["centros_de_salud"]
    
    centro_elegido = st.selectbox("1. Elige un centro de salud:", list(centros_de_salud_categoria.keys()))
    if centro_elegido:
        especialidades_disponibles = centros_de_salud_categoria[centro_elegido]
        especialidad_elegida = st.selectbox("2. Elige una especialidad:", especialidades_disponibles)
        if st.button("Generar mi código anónimo"):
            codigo = generar_codigo_aleatorio()
            st.session_state.codigo_generado = {"codigo": codigo, "centro": centro_elegido, "especialidad": especialidad_elegida}
            st.rerun()
    st.markdown("---")
    if st.button("⬅️ Volver al chat principal"):
        st.session_state.view = 'chat'
        st.rerun() 
    if 'codigo_generado' in st.session_state and st.session_state.codigo_generado:
        info = st.session_state.codigo_generado
        st.success("¡Tu código ha sido generado con éxito!")
        st.markdown(f"""
        **Tu código de turno anónimo es:**
        ## <p style='text-align: center; color: #007bff;'>{info['codigo']}</p>
        **Próximos pasos:**
        1.  Guarda este código (anótalo o sácale una captura).
        2.  Dirígete a **{info['centro']}**.
        3.  Presenta este código en recepción para tu turno de **{info['especialidad']}**.
        *No se te pedirá ningún dato personal hasta que llegues al centro de salud.*
        """, unsafe_allow_html=True)
        st.balloons()
        del st.session_state.codigo_generado


# --- CEREBRO HÍBRIDO ---
def obtener_respuesta_hibrida(query, categoria_seleccionada):
    query_minusculas = query.lower()
    
    if "turno" in query_minusculas:
        return None, "turno"
        
    preguntas_offline = st.session_state.contenido_dinamico[categoria_seleccionada]["preguntas_frecuentes"]
    for palabra, respuesta in preguntas_offline.items():
        if palabra in query_minusculas: 
            return respuesta, "offline"
    
    if online_mode_ready and model:
        try:
            system_prompt = st.session_state.contenido_dinamico[categoria_seleccionada]["system_prompt"]
            full_prompt = f"{system_prompt} Responde a la siguiente consulta del usuario: {query}"
            response = model.generate_content(full_prompt)
            respuesta_online = response.text
            st.session_state.contenido_dinamico[categoria_seleccionada]["preguntas_frecuentes"][query_minusculas] = respuesta_online
            return respuesta_online, "online"
        except Exception as e: 
            return f"Hubo un problema al contactar a la IA. Error técnico: {e}", "error"
    
    return "No encontré una respuesta y el modo online no está activo o falló.", "error"


# --- INTERFAZ PRINCIPAL ---
def get_image_as_base_64(file):
    try:
        with open(file, "rb") as f: data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError: return None

# --- NAVEGACIÓN Y ESTADO ---
if 'view' not in st.session_state: st.session_state.view = 'chat'
if 'categoria' not in st.session_state: st.session_state.categoria = "Salud Sexual"
if 'historial' not in st.session_state: st.session_state.historial = []
if 'contenido_dinamico' not in st.session_state: st.session_state.contenido_dinamico = CONTENIDO_CATEGORIAS_BASE

st.sidebar.title("Secciones")
categoria_seleccionada = st.sidebar.selectbox(
    "Elige un área de consulta:",
    list(st.session_state.contenido_dinamico.keys())
)

st.sidebar.markdown("---")
with st.sidebar.expander("Historial de Consultas", expanded=True):
    if not st.session_state.historial:
        st.write("Aún no hay consultas.")
    else:
        for i, (pregunta, _) in enumerate(st.session_state.historial[-5:]):
            st.info(f"{pregunta[:35]}...")

if categoria_seleccionada != st.session_state.categoria:
    st.session_state.categoria = categoria_seleccionada
    st.session_state.view = 'chat'
    st.session_state.historial = [] 
    st.rerun()

info_categoria = st.session_state.contenido_dinamico[st.session_state.categoria]
img_dark_base64 = get_image_as_base_64("logo_dark.png")
img_light_base64 = get_image_as_base_64("logo_light.png")

if img_dark_base64 and img_light_base64:
    st.markdown(
        f"""
        <div class="custom-header">
            <!-- Dos logos: uno para cada tema -->
            <img class="logo-dark" src="data:image/png;base64,{img_dark_base64}">
            <img class="logo-light" src="data:image/png;base64,{img_light_base64}">
            <div>
                <h2 class="title-text">IntegraSalud SDE</h2>
                <p class="caption-text">{info_categoria["titulo"]}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.title(f"💬 {info_categoria['titulo']}")
    st.warning("Asegúrate de tener 'logo_dark.png' y 'logo_light.png' en la carpeta.")

# --- Lógica de Renderizado ---
if st.session_state.view == 'turno':
    mostrar_interfaz_de_turnos(st.session_state.categoria)
else:
    st.markdown("<p style='text-align: center;'>Bienvenido/a a IntegraSalud, un espacio seguro para tus dudas.</p>", unsafe_allow_html=True)
    # Mostrar el historial de chat como burbujas
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for i, (pregunta, respuesta) in enumerate(st.session_state.historial):
        st.markdown(f'<div class="chat-bubble user-bubble">{pregunta}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-bubble assistant-bubble">{respuesta}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    placeholder = info_categoria["placeholder"]
    
    with st.form(key="chat_form", clear_on_submit=True):
        user_query = st.text_input(
            "Escribe tu consulta...", 
            placeholder=placeholder, 
            label_visibility="collapsed"
        )
        submitted = st.form_submit_button("Consultar")

    if submitted and user_query:
        respuesta, metodo = obtener_respuesta_hibrida(user_query, st.session_state.categoria)
        if metodo == "turno":
            st.session_state.view = 'turno'
        else:
            st.session_state.historial.append((user_query, respuesta))
        st.rerun()

# --- PIE DE PÁGINA ---
st.markdown("---")

st.markdown("<p class='footer-text'>Desarrollado con ❤️ por Santino, Virginia, Candela y Milagros</p>", unsafe_allow_html=True)
