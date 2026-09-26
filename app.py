import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓ DE LA PÀGINA ---
st.set_page_config(
    page_title="Videoteca & Estadístiques - C.F. Ginesta",
    page_icon="⚽",
    layout="wide"
)

# --- ESTIL I COLORS PERSONALITZATS (Basat en la teva app vella) ---
st.markdown("""
    <style>
    /* Fons general de l'aplicació */
    .stApp {
        background-color: #f7f5fa;
        color: #2b1b3d;
    }
    
    /* Textos generals visibles */
    h1, h2, h3, h4, h5, h6, p, label {
        color: #2b1b3d !important;
    }
    
    /* Botons principals (lila amb lletra blanca) */
    .stButton>button, .stButton>button * {
        color: white !important;
        background-color: #5c2d73;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #4a2858;
    }
    
    /* --- CAIXA DE CONTRASENYA (Fons blanc i text fosc ben visible) --- */
    .stTextInput>div>div>input {
        background-color: white !important;
        color: #2b1b3d !important;
        border: 2px solid #5c2d73 !important;
        border-radius: 8px !important;
    }
    
    /* --- SELECTOR DE PARTITS (Fons lila i lletres blanques) --- */
    div[data-baseweb="select"] > div {
        background-color: #5c2d73 !important;
        color: white !important;
        border-color: #4a2858 !important;
        border-radius: 8px;
    }
    
    /* Text interior del selectbox i icones */
    div[data-baseweb="select"] span, div[data-baseweb="select"] svg {
        color: white !important;
        fill: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓ DE SUPABASE ---
SUPABASE_URL = "https://bufdixztdxrzyrdmueuk.supabase.co"
SUPABASE_KEY = "sb_publishable_HTicRAPZhBwmC_rcpnMIbQ_Ooy7DurR"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- SISTEMA DE DOBLE CLAU D'ACCÉS ---
def check_access():
    if "auth_level" not in st.session_state:
        st.session_state["auth_level"] = None

    if st.session_state["auth_level"] is None:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            try:
                st.image("logo.png", width=160)
            except:
                pass
                
        st.title("🔒 Accés Restringit - C.F. Ginesta Cadet F11")
        st.write("Espai privat per a les famílies i cos tècnic. Introdueix la contrasenya:")
        
        input_pass = st.text_input("Contrasenya:", type="password")
        if st.button("Entrar"):
            if input_pass == "admin2026":  # <-- Clau d'administració (desbloqueja tot)
                st.session_state["auth_level"] = "admin"
                st.rerun()
            elif input_pass == "ginesta2026":  # <-- Clau de famílies (vídeos i stats)
                st.session_state["auth_level"] = "family"
                st.rerun()
            else:
                st.error("❌ Contrasenya incorrecta. Torna-ho a provar.")
        return False
    return True

if not check_access():
    st.stop()

# --- BARRA LATERAL (Informació de sessió i tancar) ---
with st.sidebar:
    st.write(f"Mode actual: **{st.session_state['auth_level'].upper()}**")
    if st.button("Tancar sessió"):
        st.session_state["auth_level"] = None
        st.rerun()

# --- APLICACIÓ PRINCIPAL ---
def main():
    # --- CAPÇALERA AMB EL LOGO DEL GINESTA ---
    col1, col2 = st.columns([1, 4])
    with col1:
        try:
            st.image("logo.png", width=100)
        except:
            st.write("⚽")
    with col2:
        st.title("C.F. Ginesta - Cadet F11")
        st.markdown("*Videoteca Oficial & Estadístiques de la Temporada*")

    st.divider()

    # --- DEFINIR PESTANYES SEGONS EL ROL ---
    if st.session_state["auth_level"] == "admin":
        tab_videos, tab_stats, tab_admin = st.tabs(["🎬 Videoteca", "📊 Estadístiques", "⚙️ Administració"])
    else:
        tab_videos, tab_stats = st.tabs(["🎬 Videoteca", "📊 Estadístiques"])

    # ==========================================
    # PESTANYA 1: VÍDEOS DELS PARTITS
    # ==========================================
    with tab_videos:
        st.subheader("📺 Partits Gravats")
        
        partits = []
        try:
            response = supabase.table("partits").select("*").order("data", desc=True).execute()
            partits = response.data
        except Exception as e:
            st.error(f"❌ Error en carregar els partits de Supabase: {e}")

        if not partits:
            st.warning("Encara no hi ha partits registrats a la base de dades.")
        else:
            opcions_partits = {f"{p.get('data', '')} - {p.get('titol', 'Sense títol')} (Jornada {p.get('jornada', '')})": p for p in partits}
            
            partit_seleccionat_str = st.selectbox("Selecciona un partit per veure:", list(opcions_partits.keys()))
            partit_actual = opcions_partits[partit_seleccionat_str]
            
            st.markdown(f"### 🏟️ {partit_actual.get('titol')}")
            st.markdown(f"📅 **Data:** {partit_actual.get('data')} &nbsp;&nbsp;|&nbsp;&nbsp; 🏆 **Jornada:** {partit_actual.get('jornada')}")
            
            # Nota: Accepta tant 'video_url' com 'enllaç_video' per evitar fallos
            video_url = partit_actual.get('video_url') or partit_actual.get('enllaç_video')
            if video_url:
                st.video(video_url)
            else:
                st.warning("⚠️ El vídeo d'aquest partit encara no està disponible.")

    # ==========================================
    # PESTANYA 2: ESTADÍSTIQUES I GOLEJADORES
    # ==========================================
    with tab_stats:
        st.subheader("📊 Resum i Estadístiques de l'Equip (2x40 min)")
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric(label="Partits Jugats", value="12")
        with col_b:
            st.metric(label="Gols a Favor", value="34")
        with col_c:
            st.metric(label="Gols en Contra", value="12")

        st.markdown("---")

        st.markdown("### 🧤 Rendiment de Porteria (Clean Sheets)")
        col_porteria, _ = st.columns([1, 1])
        with col_porteria:
            fig_clean_sheets = px.pie(
                names=["Porteries a Zero", "Partits amb Gols Encaixats"],
                values=[7, 5],
                hole=0.6,
                color_discrete_sequence=["#5c2d73", "#d7bde2"]
            )
            fig_clean_sheets.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=240)
            st.plotly_chart(fig_clean_sheets, use_container_width=True)

        st.markdown("---")

        st.markdown("### ⏱️ Anàlisi Tàctica per Trams de Partit (8 blocs de 10 min)")
        col_gols_favor, col_gols_contra = st.columns(2)

        with col_gols_favor:
            st.markdown("##### ⚽ Gols a Favor (Marcats)")
            trams_favor_df = pd.DataFrame({
                "Tram": ["0'-10'", "10'-20'", "20'-30'", "30'-40'", "40'-50'", "50'-60'", "60'-70'", "70'-80'"],
                "Gols": [3, 5, 4, 6, 2, 5, 4, 5]
            })
            fig_favor = px.bar(trams_favor_df, x="Tram", y="Gols", color_discrete_sequence=["#5c2d73"])
            fig_favor.update_layout(margin=dict(t=10, b=0, l=0, r=0), height=250)
            st.plotly_chart(fig_favor, use_container_width=True)

        with col_gols_contra:
            st.markdown("##### 🛡️ Gols en Contra (Encaixats)")
            trams_contra_df = pd.DataFrame({
                "Tram": ["0'-10'", "10'-20'", "20'-30'", "30'-40'", "40'-50'", "50'-60'", "60'-70'", "70'-80'"],
                "Gols": [2, 1, 3, 2, 1, 0, 2, 1]
            })
            fig_contra = px.bar(trams_contra_df, x="Tram", y="Gols", color_discrete_sequence=["#a569bd"])
            fig_contra.update_layout(margin=dict(t=10, b=0, l=0, r=0), height=250)
            st.plotly_chart(fig_contra, use_container_width=True)

        st.markdown("---")

        st.markdown("### ⚽ Golejadores de l'Equip (Llista No Competitiva)")
        golejadores_data = [
            {"nom": "Clàudia", "gols": 8},
            {"nom": "Júlia", "gols": 6},
            {"nom": "Martina", "gols": 5},
            {"nom": "Berta", "gols": 4},
            {"nom": "Carla", "gols": 4},
            {"nom": "Aina", "gols": 3},
            {"nom": "Noa", "gols": 2}
        ]

        cols = st.columns(3)
        for i, jugadora in enumerate(golejadores_data):
            with cols[i % 3]:
                st.markdown(f"""
                    <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 5px solid #5c2d73; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                        <h4 style="margin: 0; color: #5c2d73;">{jugadora['nom']}</h4>
                        <p style="margin: 5px 0 0 0; font-size: 16px; color: #2b1b3d !important;">⚽ <b>{jugadora['gols']}</b> gols</p>
                    </div>
                """, unsafe_allow_html=True)

    # ==========================================
    # PESTANYA 3: ADMINISTRACIÓ (Només ADMIN)
    # ==========================================
    if st.session_state["auth_level"] == "admin":
        with tab_admin:
            st.subheader("⚙️ Panell d'Administració i Gestió")
            st.markdown("Des d'aquí pots penjar nous partits directament a la base de dades de Supabase.")

            st.markdown("#### ➕ Afegir Nou Partit")
            with st.form("form_nou_partit"):
                nou_titol = st.text_input("Títol del Partit (Ex: C.F. Ginesta vs CE Manresa)")
                nova_jornada = st.number_input("Número de Jornada", min_value=1, max_value=38, value=1)
                nova_data = st.date_input("Data del Partit")
                nou_video_url = st.text_input("Enllaç del Vídeo (YouTube, Drive, etc.)")
                
                submit_partit = st.form_submit_button(label="Guardar Partit a Supabase")

                if submit_partit:
                    if nou_titol and nou_video_url:
                        try:
                            data_a_inserir = {
                                "titol": nou_titol,
                                "jornada": int(nova_jornada),
                                "data": str(nova_data),
                                "video_url": nou_video_url
                            }
                            supabase.table("partits").insert(data_a_inserir).execute()
                            st.success("🎉 Partit afegit correctament a Supabase!")
                        except Exception as e:
                            st.error(f"❌ Error al guardar el partit: {e}")
                    else:
                        st.warning("⚠️ Si us plau, omple almenys el títol i l'enllaç del vídeo.")

# Executar aplicació
if check_access():
    main()
