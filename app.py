import streamlit as st
import google.generativeai as genai
import time
import random
import base64
from pathlib import Path

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="IntegraSalud SDE", page_icon="favicon.png", layout="centered")

# -----------------------------------------------------------------------------
# PEGA AQUÍ TU NUEVA Y SECRETA API KEY
# -----------------------------------------------------------------------------
api_key = st.secrets.get("GOOGLE_API_KEY")
# -----------------------------------------------------------------------------

# --- LÓGICA ONLINE ---
model = None
online_mode_ready = False 

if api_key == st.secrets.get("GOOGLE_API_KEY"):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        online_mode_ready = True
    except Exception as e:
        st.error(f"Error al configurar la API de Google. El modo online no funcionará.")
        st.exception(e) 
else:
    st.warning("API Key no configurada. El modo online está desactivado.")


# --- CONTENIDO DE LAS CATEGORÍAS (Base estática) ---
CONTENIDO_CATEGORIAS_BASE = {
    "Salud Sexual": {
        "emoji": "💬",
        "titulo": "Asistente de Salud Sexual 🩺💊",
        "placeholder": "Prueba con 'ITS' o 'turno'...",
        "preguntas_frecuentes": {
            "its": """
            Las Infecciones de Transmisión Sexual (ITS) se transmiten de una persona a otra durante las relaciones sexuales (vaginales, anales u orales). Algunas de las más comunes son el VPH, la sífilis, la gonorrea, la clamidia y el VIH.

            Muchas ITS no presentan síntomas visibles, por lo que una persona puede tener una y no saberlo. La forma más efectiva de prevenirlas es usando **preservativo** en todas las relaciones sexuales. También es fundamental realizarse controles médicos periódicos.

            **Recuerda: Si tienes dudas, síntomas o simplemente quieres controlarte, consulta a un profesional de la salud.**
            """,
            "ets": """
            El término "Enfermedades de Transmisión Sexual" (ETS) se usaba antiguamente. Hoy se prefiere "Infecciones de Transmisión Sexual" (ITS) porque describe mejor la situación: una persona puede tener una infección (y transmitirla) sin necesariamente desarrollar los síntomas de una "enfermedad".

            El concepto de prevención es exactamente el mismo: el uso de preservativo es clave para reducir el riesgo.

            **Para un diagnóstico correcto y tratamiento, es fundamental que consultes a un médico/a.**
            """,
            "anticonceptivos": """
            Existen diversos métodos anticonceptivos para planificar la familia y prevenir embarazos no intencionados. Se dividen principalmente en:
            - **De barrera:** Preservativo (el único que también previene ITS), diafragma.
            - **Hormonales:** Pastillas anticonceptivas, inyecciones mensuales, implante subdérmico (el "chip"), DIU hormonal.
            - **DIU de Cobre:** Un dispositivo intrauterino que no contiene hormonas.
            - **De emergencia:** La pastilla del día después, que debe usarse solo en casos de emergencia y no como método regular.

            **La elección del método es muy personal y depende de tu cuerpo y estilo de vida. Un/a ginecólogo/a o profesional de la salud te puede asesorar para encontrar el más adecuado para ti.**
            """,
            "preservativo": """
            El preservativo, también conocido como condón, es el método más eficaz para la **doble protección**: previene tanto los embarazos no intencionados como la transmisión de la gran mayoría de las Infecciones de Transmisión Sexual (ITS), incluyendo el VIH.

            Debe usarse correctamente, colocándolo antes de cualquier penetración y retirándolo al finalizar. En Argentina, puedes conseguir preservativos de forma gratuita en hospitales, salitas y centros de salud públicos.
            """,
            "consentimiento": """
            El consentimiento en las relaciones sexuales es fundamental e innegociable. Significa que todas las personas involucradas están de acuerdo de forma **entusiasta, voluntaria, clara y consciente** en participar en una actividad sexual.

            **Puntos Clave del Consentimiento:**
            - Debe ser explícito: ¡El silencio no es un sí!
            - Se puede retirar en cualquier momento, sin importar lo que haya pasado antes.
            - No se puede dar si una persona está dormida, inconsciente o bajo los efectos del alcohol o drogas.
            - Que hayas dicho que sí antes, no significa que digas que sí ahora.

            **Sin consentimiento, cualquier acto sexual es abuso.**
            """
        },
        "system_prompt": """
            **Tu Identidad:** Eres 'IntegraSalud', un asistente virtual educativo sobre **Salud Sexual y Reproductiva**.
            **Tu Misión:** Proporcionar información clara, precisa, científica, inclusiva y libre de prejuicios.
            **REGLAS:** No actúes como un médico. Siempre recomienda consultar a un profesional. Si te preguntan por un turno, indica que escriban la palabra 'turno'.
        """
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
            **Tu Misión:** Ofrecer un espacio seguro para que los usuarios se expresen. Proporciona información general y estrategias de afrontamiento.
            **REGLAS:** No eres un terapeuta. Jamás diagnostiques. Anima siempre al usuario a buscar ayuda profesional (psicólogo/a, psiquiatra) como el paso más importante. Tu tono debe ser calmado y empático.
        """
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
            Las carbohidratos son la principal fuente de combustible del cuerpo, especialmente para el cerebro y los músculos. No todos son iguales:
            - **Complejos:** Se absorben lentamente, dando energía sostenida. Se encuentran en granos integrales, avena, legumbres y verduras.
            - **Simples:** Se absorben rápido, dando un pico de energía. Están en azúcares, dulces y harinas refinadas.

            Una dieta saludable prioriza los carbohidratos complejos.

            **Un/a nutricionista puede ayudarte a equilibrar tu consumo de carbohidratos de forma saludable.**
            """
        },
        "system_prompt": """
            **Tu Identidad:** Eres 'IntegraSalud', un asistente virtual educativo sobre **Nutrición y Alimentación Saludable**.
            **Tu Misión:** Proporcionar información basada en evidencia científica sobre alimentos y hábitos saludables.
            **REGLAS:** No eres un nutricionista. No puedes crear planes de dieta personalizados. Siempre recomienda consultar a un nutricionista o médico para obtener asesoramiento personalizado, especialmente si existen condiciones médicas.
        """
    }
}

# --- LÓGICA DE TURNOS ANÓNIMOS ---
CENTROS_DE_SALUD = {
    "Upa N° 2 B° Cáceres (Capital)": ["Ginecología", "Clínica Médica", "Testeo Rápido ITS"],
    "CePSI 'Eva Perón' (Capital)": ["Salud Adolescente", "Ginecología"],
    "Hospital Regional 'Dr. Ramón Carrillo'": ["Ginecología", "Urología", "Infectología"],
    "CISB La Banda": ["Clínica Médica", "Ginecología", "Testeo Rápido ITS"]
}

def generar_codigo_aleatorio():
    palabras = ["LUNA", "SOL", "RIOJA", "SALTA", "NORTE", "CEIBO", "FLOR", "PAZ"]
    numero = random.randint(100, 999)
    return f"{random.choice(palabras)}-{random.choice(palabras)}-{numero}"

def mostrar_interfaz_de_turnos():
    st.info("#### 🗓️ Generador de Turno Anónimo")
    centro_elegido = st.selectbox("1. Elige un centro de salud:", list(CENTROS_DE_SALUD.keys()))
    if centro_elegido:
        especialidades_disponibles = CENTROS_DE_SALUD[centro_elegido]
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
        st.markdown(f"<p style='text-align: center; color: #007bff;'>{info['codigo']}</p>", unsafe_allow_html=True)
        st.balloons()
        del st.session_state.codigo_generado


# --- CEREBRO HÍBRIDO ---
def obtener_respuesta_hibrida(query, categoria_seleccionada):
    query_minusculas = query.lower()
    
    if categoria_seleccionada == "Salud Sexual" and "turno" in query_minusculas:
        return None, "turno"
        
    # CAMBIO: Busca en la base de datos dinámica de la sesión
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

            # --- LÓGICA DE AUTO-APRENDIZAJE ---
            # Guarda la nueva respuesta en la base de datos de la sesión actual
            st.session_state.contenido_dinamico[categoria_seleccionada]["preguntas_frecuentes"][query_minusculas] = respuesta_online
            # --- FIN DE LA LÓGICA ---

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
if 'view' not in st.session_state:
    st.session_state.view = 'chat'
if 'respuesta_actual' not in st.session_state:
    st.session_state.respuesta_actual = None
if 'categoria' not in st.session_state:
    st.session_state.categoria = "Salud Sexual"
if 'historial' not in st.session_state:
    st.session_state.historial = []
# CAMBIO: Inicializa la base de datos dinámica si no existe
if 'contenido_dinamico' not in st.session_state:
    st.session_state.contenido_dinamico = CONTENIDO_CATEGORIAS_BASE


# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.title("Secciones")
categoria_seleccionada = st.sidebar.selectbox(
    "Elige un área de consulta:",
    list(st.session_state.contenido_dinamico.keys())
)

st.sidebar.markdown("---")
st.sidebar.subheader("Historial de Consultas")
if not st.session_state.historial:
    st.sidebar.write("Aún no hay consultas.")
else:
    for i, (pregunta, respuesta) in enumerate(st.session_state.historial):
        with st.sidebar.expander(f"Consulta #{i+1}: {pregunta[:30]}..."):
            st.markdown(f"**Tú:** {pregunta}")
            st.markdown(f"**Asistente:** {respuesta}")

# --- Lógica de actualización de estado ---
if categoria_seleccionada != st.session_state.categoria:
    st.session_state.categoria = categoria_seleccionada
    st.session_state.respuesta_actual = None
    st.session_state.view = 'chat'
    st.session_state.historial = [] 
    st.rerun()

# --- Encabezado ---
info_categoria = st.session_state.contenido_dinamico[st.session_state.categoria]
img_base64 = get_image_as_base_64("logo.png")

# CAMBIO: Se usa st.markdown con HTML y CSS para un control total de la alineación
if img_base64:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <img src="data:image/png;base64,{img_base64}" width="250">
            <div style="margin-left: 20px;">
                <h2 style="margin-bottom: 0;">IntegraSalud SDE</h2>
                <p style="margin-top: 0; color: grey;">{info_categoria['titulo']}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    # Fallback si el logo no se encuentra, para que la app no se rompa
    st.header("IntegraSalud SDE")
    st.caption(info_categoria["titulo"])
    st.warning("Logo no encontrado.")


st.markdown("---")
st.markdown("Bienvenido/a a IntegraSalud, un espacio seguro para tus dudas.")

# --- Lógica de Renderizado ---
if st.session_state.view == 'turno':
    mostrar_interfaz_de_turnos()
else: # Vista 'chat'
    placeholder = info_categoria["placeholder"]
    
    with st.form(key="chat_form", clear_on_submit=True):
        user_query = st.text_input(
            "Escribe tu consulta...", 
            placeholder=placeholder, 
            label_visibility="collapsed"
        )
        submitted = st.form_submit_button("Consultar")

    if submitted:
        if user_query:
            respuesta, metodo = obtener_respuesta_hibrida(user_query, st.session_state.categoria)
            if metodo == "turno":
                st.session_state.view = 'turno'
            else:
                st.session_state.respuesta_actual = (respuesta, metodo)
                st.session_state.historial.append((user_query, respuesta))
        else:
            st.warning("Por favor, escribe tu consulta.")
            st.session_state.respuesta_actual = None
        st.rerun() 
            
    if st.session_state.respuesta_actual:
        respuesta, metodo = st.session_state.respuesta_actual
        if metodo == "offline":
            st.success("✔️ Respuesta Rápida (Offline)")
            st.markdown(respuesta)
        elif metodo == "online":
            st.info("🌐 Respuesta Detallada (Online)")
            st.markdown(respuesta)
        else: 
            st.error("Hubo un problema")
            st.markdown(respuesta)

# --- PIE DE PÁGINA ---
st.markdown("---")
st.markdown("<p class='footer-text'>Desarrollado con ❤️ por Santino, Virginia, Candela y Milagros</p>", unsafe_allow_html=True)

