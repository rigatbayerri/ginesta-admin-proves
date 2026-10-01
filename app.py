import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
import os
import time
import base64
import requests
import datetime

# --- CONFIGURACIÓ DE LA PÀGINA ---
st.set_page_config(
    page_title="Videoteca & Estadístiques - C.F. Ginesta",
    page_icon="https://files.fcf.cat/escudos/clubes/escudos/00100_0001239324_GINESTA.png",
    layout="wide"
)

LOGO_URL = "https://files.fcf.cat/escudos/clubes/escudos/00100_0001239324_GINESTA.png"
DIRECCIO_CASA = "https://maps.app.goo.gl/qq7hJCHrqQv4ZVAB7"

# Funció infal·lible per convertir qualsevol imatge (local o web) a Base64
def obtenir_imatge_base64(path_o_url):
    if not path_o_url:
        return ""
    try:
        if path_o_url.startswith("http"):
            response = requests.get(path_o_url, timeout=5)
            if response.status_code == 200:
                encoded = base64.b64encode(response.content).decode()
                return f"data:image/png;base64,{encoded}"
        elif os.path.exists(path_o_url):
            with open(path_o_url, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode()
                return f"data:image/png;base64,{encoded}"
    except:
        pass
    return path_o_url

# Injectar manifest web i etiquetes d'Apple
st.markdown(f"""
    <link rel="manifest" href="data:application/manifest+json;charset=utf-8,{{
      'name': 'C.F. Ginesta Cadet F11',
      'short_name': 'Ginesta',
      'start_url': '.',
      'display': 'standalone',
      'background_color': '#f7f5fa',
      'theme_color': '#5c2d73',
      'icons': [{{'src': '{LOGO_URL}', 'sizes': '512x512', 'type': 'image/png'}}]
    }}">
    <link rel="apple-touch-icon" sizes="180x180" href="{LOGO_URL}">
    <link rel="apple-touch-icon-precomposed" href="{LOGO_URL}">
    <link rel="shortcut icon" href="{LOGO_URL}">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="C.F. Ginesta">
""", unsafe_allow_html=True)

# --- ESTIL I COLORS CORPORATIUS ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f7f5fa;
        color: #1a1a1a;
    }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, span {
        color: #1a1a1a !important;
    }
    .stButton>button, .stButton>button *, div.stFormSubmitButton>button, div.stFormSubmitButton>button * {
        color: white !important;
        background-color: #5c2d73 !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
        padding: 0.5rem 1rem !important;
    }
    .stButton>button:hover, div.stFormSubmitButton>button:hover {
        background-color: #4a2858 !important;
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stDateInput>div>div>input {
        background-color: white !important;
        color: #1a1a1a !important;
        border: 2px solid #5c2d73 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #5c2d73 !important;
        border-color: #4a2858 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] span, div[data-baseweb="select"] svg {
        color: white !important;
        fill: white !important;
    }
    div[data-baseweb="popover"] div[role="option"] {
        background-color: white !important;
        color: #1a1a1a !important;
    }
    div[data-baseweb="popover"] div[role="option"] * {
        color: #1a1a1a !important;
    }
    [data-testid="stMetricDelta"] svg {
        display: none !important;
    }
    [data-testid="stMetricDelta"] > div {
        color: #5c2d73 !important;
        background-color: transparent !important;
        font-weight: 600 !important;
        padding: 0 !important;
    }
    @media (max-width: 768px) {
        .element-container, .stColumn {
            width: 100% !important;
            flex: 100% !important;
            max-width: 100% !important;
        }
        h1 {
            font-size: 1.5rem !important;
        }
        h2 {
            font-size: 1.2rem !important;
        }
        h3 {
            font-size: 1.05rem !important;
        }
        .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            padding-top: 1rem !important;
        }
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

if not os.path.exists("escuts"):
    os.makedirs("escuts")
if not os.path.exists("fotos_partits"):
    os.makedirs("fotos_partits")

# --- SISTEMA DE DOBLE CLAU D'ACCÉS ---
def check_access():
    if "auth_level" not in st.session_state:
        st.session_state["auth_level"] = None

    if st.session_state["auth_level"] is None:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            try:
                st.image(LOGO_URL, width=130)
            except:
                pass
                
        st.title("🔒 Accés Restringit")
        st.write("Espai privat per a les famílies i cos tècnic. Introdueix la contrasenya:")
        
        input_pass = st.text_input("Contrasenya:", type="password")
        if st.button("Entrar"):
            if input_pass == "admin2026":
                st.session_state["auth_level"] = "admin"
                st.rerun()
            elif input_pass == "ginesta2026":
                st.session_state["auth_level"] = "family"
                st.rerun()
            else:
                st.error("❌ Contrasenya incorrecta.")
        return False
    return True

if not check_access():
    st.stop()

# --- BARRA LATERAL ---
with st.sidebar:
    st.write(f"Mode actual: **{st.session_state['auth_level'].upper()}**")
    if st.button("Tancar sessió"):
        st.session_state["auth_level"] = None
        st.rerun()

# --- APLICACIÓ PRINCIPAL ---
def main():
    # Capçalera 100% centrada amb disseny creatiu tipus insígnia esportiva
    escut_b64 = obtenir_imatge_base64(LOGO_URL)
    st.markdown(f"""
        <div style="text-align: center; padding: 10px 0 20px 0;">
            <div style="display: inline-block; padding: 12px; background: white; border-radius: 50%; box-shadow: 0px 4px 15px rgba(92,45,115,0.15); border: 2px solid #f0eaf5; margin-bottom: 10px;">
                <img src="{escut_b64}" style="width: 100px; height: 100px; object-fit: contain; display: block;">
            </div>
            <div style="font-size: 24px; font-weight: 900; color: #5c2d73; letter-spacing: 2px; text-transform: uppercase; margin-top: 5px;">
                CADET F11
            </div>
            <div style="font-size: 12px; font-weight: 700; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-top: 2px;">
                C.F. Ginesta
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # --- BANNER FIX GLOBAL: ORDENAT STRICTAMENT PER DATA (El més proper primer) ---
    try:
        res_cal_all = supabase.table("calendari").select("*").execute()
        if res_cal_all.data:
            def parse_data_partit(p):
                d_str = p.get('data')
                if not d_str:
                    return datetime.date.max
                try:
                    return datetime.datetime.strptime(str(d_str).strip(), "%Y-%m-%d").date()
                except:
                    return datetime.date.max

            llista_cal_per_data = sorted(res_cal_all.data, key=parse_data_partit)
            avui = datetime.date.today()
            proper_partit = None
            
            for p in llista_cal_per_data:
                d_obj = parse_data_partit(p)
                if d_obj >= avui:
                    proper_partit = p
                    break
            
            if not proper_partit and llista_cal_per_data:
                proper_partit = llista_cal_per_data[-1]

            if proper_partit:
                j_prop = proper_partit.get('jornada', '-')
                data_prop = proper_partit.get('data', '-')
                hora_prop = proper_partit.get('hora', '-')
                rival_prop = proper_partit.get('rival', '-')
                lloc_prop = proper_partit.get('lloc', 'Casa')
                escut_prop = proper_partit.get('escut_rival_url', '')
                maps_prop = proper_partit.get('maps_url', '')

                if lloc_prop == "Fora":
                    e1_nom = rival_prop
                    e1_img = obtenir_imatge_base64(escut_prop)
                    e2_nom = "C.F. Ginesta"
                    e2_img = obtenir_imatge_base64(LOGO_URL)
                else:
                    e1_nom = "C.F. Ginesta"
                    e1_img = obtenir_imatge_base64(LOGO_URL)
                    e2_nom = rival_prop
                    e2_img = obtenir_imatge_base64(escut_prop)

                img1_p = f"<img src='{e1_img}' style='width: 55px; height: 55px; object-fit: contain;'>" if e1_img else "<div style='font-size: 35px;'>🛡️</div>"
                img2_p = f"<img src='{e2_img}' style='width: 55px; height: 55px; object-fit: contain;'>" if e2_img else "<div style='font-size: 35px;'>🛡️</div>"
                maps_p_html = f"&nbsp;|&nbsp; 📍 <a href='{maps_prop}' target='_blank' style='color: #5c2d73; font-weight: bold; text-decoration: underline;'>Com arribar</a>" if maps_prop and str(maps_prop).startswith("http") else ""

                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #f7f3fb 0%, #ede4f5 100%); padding: 14px 16px; border-radius: 14px; border: 2px solid #5c2d73; margin-bottom: 20px; box-shadow: 3px 3px 10px rgba(92,45,115,0.08);">
                        <div style="font-size: 13px; font-weight: bold; color: #5c2d73; text-transform: uppercase; margin-bottom: 8px; border-bottom: 1px solid #dcd0e8; padding-bottom: 4px;">
                            ⚡ Proper Partit &nbsp;|&nbsp; Jornada {j_prop} &nbsp;|&nbsp; 📅 {data_prop} &nbsp;|&nbsp; ⏰ {hora_prop} {maps_p_html}
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div style="display: flex; align-items: center; gap: 10px; width: 42%;">
                                {img1_p}
                                <span style="font-weight: 900; font-size: 15px; color: #1a1a1a;">{e1_nom}</span>
                            </div>
                            <div style="text-align: center; width: 16%;">
                                <span style="background-color: #5c2d73; color: white; padding: 5px 12px; border-radius: 8px; font-size: 14px; font-weight: bold; display: inline-block;">VS</span>
                            </div>
                            <div style="display: flex; align-items: center; justify-content: flex-end; gap: 10px; width: 42%;">
                                <span style="font-weight: 900; font-size: 15px; color: #1a1a1a; text-align: right;">{e2_nom}</span>
                                {img2_p}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    except:
        pass

    golejadores_data = []
    try:
        res_gol = supabase.table("golejadores").select("*").order("dorsal", desc=False).execute()
        golejadores_data = res_gol.data
    except:
        pass

    if not golejadores_data:
        golejadores_data = [
            {"nom": "Clàudia", "dorsal": 10, "gols": 8, "rol": "Jugadora", "grogues": 1, "vermelles": 0, "gols_encaixats": 0, "titularitats": 10, "partits_jugats": 12},
            {"nom": "Júlia", "dorsal": 7, "gols": 6, "rol": "Jugadora", "grogues": 0, "vermelles": 0, "gols_encaixats": 0, "titularitats": 9, "partits_jugats": 11},
            {"nom": "Martina", "dorsal": 8, "gols": 5, "rol": "Jugadora", "grogues": 2, "vermelles": 0, "gols_encaixats": 0, "titularitats": 11, "partits_jugats": 12},
            {"nom": "Berta", "dorsal": 11, "gols": 4, "rol": "Jugadora", "grogues": 0, "vermelles": 0, "gols_encaixats": 0, "titularitats": 8, "partits_jugats": 10},
            {"nom": "Carla", "dorsal": 14, "gols": 4, "rol": "Jugadora", "grogues": 1, "vermelles": 0, "gols_encaixats": 0, "titularitats": 7, "partits_jugats": 9},
            {"nom": "Aina", "dorsal": 6, "gols": 3, "rol": "Jugadora", "grogues": 0, "vermelles": 0, "gols_encaixats": 0, "titularitats": 8, "partits_jugats": 10},
            {"nom": "Noa", "dorsal": 1, "gols": 0, "rol": "Portera", "grogues": 0, "vermelles": 0, "gols_encaixats": 5, "titularitats": 12, "partits_jugats": 12}
        ]

    golejadores_data = sorted(golejadores_data, key=lambda x: int(x.get('dorsal', 0) or 0))

    try:
        res_extra = supabase.table("estadistiques_generals").select("*").execute()
        if res_extra.data:
            st_data = res_extra.data[0]
            n_partits = st_data.get("partits_jugats", 12)
            porteries_zero = st_data.get("porteries_zero", 7)
            gols_propia_porta = st_data.get("gols_propia_porta", 0)
            gols_contra_total = st_data.get("gols_contra", 5)
        else:
            n_partits, porteries_zero, gols_propia_porta, gols_contra_total = 12, 7, 1, 5
    except:
        n_partits, porteries_zero, gols_propia_porta, gols_contra_total = 12, 7, 1, 5

    gols_jugadores_total = sum(int(j.get('gols', 0) or 0) for j in golejadores_data if j.get('rol', 'Jugadora') == 'Jugadora')
    g_favor_total = gols_jugadores_total + int(gols_propia_porta)

    total_grogues = sum(int(j.get('grogues', 0) or 0) for j in golejadores_data)
    total_vermelles = sum(int(j.get('vermelles', 0) or 0) for j in golejadores_data)

    def sincronitzar_estadistiques_generals(nous_partits, noves_p_zero, nous_propia, nous_contra):
        try:
            actual_gols_jugadores = sum(int(j.get('gols', 0) or 0) for j in golejadores_data if j.get('rol', 'Jugadora') == 'Jugadora')
            supabase.table("estadistiques_generals").delete().neq("id", 0).execute()
            supabase.table("estadistiques_generals").insert({
                "partits_jugats": int(nous_partits),
                "gols_favor": int(actual_gols_jugadores + int(nous_propia)),
                "gols_contra": int(nous_contra),
                "porteries_zero": int(noves_p_zero),
                "gols_propia_porta": int(nous_propia)
            }).execute()
        except Exception as e:
            st.error(f"❌ Error en sincronitzar estadístiques: {e}")

    # PESTANYES PRINCIPALS
    if st.session_state["auth_level"] == "admin":
        tab_calendari, tab_videos, tab_plantilla, tab_stats, tab_admin = st.tabs(["📅 Calendari", "🎬 Videoteca", "👥 Plantilla", "📊 Estadístiques", "⚙️ Admin"])
    else:
        tab_calendari, tab_videos, tab_plantilla, tab_stats = st.tabs(["📅 Calendari", "🎬 Videoteca", "👥 Plantilla", "📊 Estadístiques"])

    # PESTANYA 1: CALENDARI PÚBLIC
    with tab_calendari:
        st.subheader("📅 Calendari Oficial")
        calendari_data = []
        try:
            res_cal = supabase.table("calendari").select("*").execute()
            calendari_data = res_cal.data
            calendari_data = sorted(calendari_data, key=lambda x: int(x.get('jornada', 1) or 1))
        except:
            pass

        if not calendari_data:
            st.warning("No hi ha partits al calendari.")
        else:
            for partit in calendari_data:
                jornada = partit.get('jornada', '-')
                data = partit.get('data', '-')
                hora = partit.get('hora', '-')
                rival = partit.get('rival', '-')
                lloc = partit.get('lloc', 'Casa')
                escut_path = partit.get('escut_rival_url', '')
                resultat_cal = partit.get('resultat', '')
                maps_url = partit.get('maps_url', '')

                if not resultat_cal or str(resultat_cal).strip() == "" or str(resultat_cal).lower() == "none":
                    text_marcador = "VS"
                else:
                    text_marcador = str(resultat_cal)

                if lloc == "Fora":
                    eq1_nom = rival
                    eq1_img_b64 = obtenir_imatge_base64(escut_path)
                    eq2_nom = "C.F. Ginesta"
                    eq2_img_b64 = obtenir_imatge_base64(LOGO_URL)
                else:
                    eq1_nom = "C.F. Ginesta"
                    eq1_img_b64 = obtenir_imatge_base64(LOGO_URL)
                    eq2_nom = rival
                    eq2_img_b64 = obtenir_imatge_base64(escut_path)

                img1_html = f"<img src='{eq1_img_b64}' style='width: 65px; height: 65px; object-fit: contain;'>" if eq1_img_b64 else "<div style='font-size: 40px;'>🛡️</div>"
                img2_html = f"<img src='{eq2_img_b64}' style='width: 65px; height: 65px; object-fit: contain;'>" if eq2_img_b64 else "<div style='font-size: 40px;'>🛡️</div>"

                maps_html = f"&nbsp;|&nbsp; 📍 <a href='{maps_url}' target='_blank' style='color: #5c2d73; font-weight: bold; text-decoration: underline;'>Com arribar (Google Maps)</a>" if maps_url and str(maps_url).startswith("http") else ""

                st.markdown(f"""
                    <div style="background-color: white; padding: 12px 16px; border-radius: 12px; border: 1px solid #e0d8e8; margin-bottom: 10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.04);">
                        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #5c2d73; font-weight: bold; border-bottom: 1px solid #f2ecf8; padding-bottom: 6px; margin-bottom: 8px;">
                            <span>Jornada {jornada} &nbsp;|&nbsp; 📅 {data} &nbsp;|&nbsp; ⏰ {hora} {maps_html}</span>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div style="display: flex; align-items: center; gap: 12px; width: 40%;">
                                {img1_html}
                                <span style="font-weight: 900; font-size: 15px; color: #1a1a1a;">{eq1_nom}</span>
                            </div>
                            <div style="text-align: center; width: 20%;">
                                <span style="background-color: #f0eaf5; color: #1a1a1a; padding: 6px 14px; border-radius: 8px; font-size: 16px; font-weight: 900; border: 1px solid #d5c8e3; display: inline-block;">{text_marcador}</span>
                            </div>
                            <div style="display: flex; align-items: center; justify-content: flex-end; gap: 12px; width: 40%;">
                                <span style="font-weight: 900; font-size: 15px; color: #1a1a1a; text-align: right;">{eq2_nom}</span>
                                {img2_html}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # PESTANYA 2: VIDEOTECA AMB SUBPESTANYES INTERNES (VÍDEOS / FOTOS)
    with tab_videos:
        st.subheader("📺 Videoteca & Galeria de Partits")
        partits = []
        try:
            response = supabase.table("partits").select("*").order("data", desc=True).execute()
            partits = response.data
        except Exception as e:
            st.error(f"❌ Error: {e}")

        if not partits:
            st.warning("Encara no hi ha partits registrats.")
        else:
            opcions_partits = {}
            for p in partits:
                jornada_val = p.get('jornada')
                j_str = f"J.{jornada_val}" if jornada_val and str(jornada_val).strip() else "J-"
                titol_val = p.get('titol', 'Partit')
                res_val = p.get('resultat')
                res_str = str(res_val) if res_val and str(res_val).strip().lower() != "none" else "vs"
                opcions_partits[f"{j_str} - {titol_val} ({res_str})"] = p

            partit_seleccionat_str = st.selectbox("Selecciona un partit:", list(opcions_partits.keys()))
            partit_actual = opcions_partits[partit_seleccionat_str]
            
            rival = partit_actual.get('rival', 'Rival')
            lloc = partit_actual.get('lloc', 'Casa')
            fotos_str = partit_actual.get('fotos_partit_urls', '')
            
            st.markdown("---")
            st.markdown(f"### 🏟️ {partit_actual.get('titol')}")
            jornada_mostra = partit_actual.get('jornada')
            jornada_txt_mostra = str(jornada_mostra) if jornada_mostra and str(jornada_mostra).strip() else "-"
            st.markdown(f"📅 **Data:** {partit_actual.get('data')} &nbsp;|&nbsp; 🏆 **Jornada:** {jornada_txt_mostra} &nbsp;|&nbsp; 📍 **Lloc:** {lloc} &nbsp;|&nbsp; 🛡️ **Rival:** {rival}")
            
            targetes_partit_str = partit_actual.get('targetes_partit', '')
            if targetes_partit_str:
                st.markdown(f"🟨 **Targetes del partit:** {targetes_partit_str}")

            st.markdown("---")

            sub_vid, sub_fot = st.tabs(["📺 Vídeo del Partit", "📸 Galeria de Fotos"])

            with sub_vid:
                video_url = partit_actual.get('video_url') or partit_actual.get('enllaç_video')
                if video_url and str(video_url).startswith("http"):
                    try:
                        st.video(video_url)
                    except Exception:
                        st.warning("⚠️ L'enllaç del vídeo no és compatible o no està accessible.")
                else:
                    st.warning("⚠️ El vídeo d'aquest partit encara no està disponible o l'enllaç no és vàlid.")

            with sub_fot:
                if fotos_str:
                    lletres_fotos = [f.strip() for f in fotos_str.split(",") if f.strip()]
                    if lletres_fotos:
                        for f_path in lletres_fotos:
                            if os.path.exists(f_path):
                                st.image(f_path, use_container_width=True)
                    else:
                        st.info("No hi ha fotos disponibles per a aquest partit.")
                else:
                    st.info("No hi ha fotos disponibles per a aquest partit.")

    # PESTANYA 3: PLANTILLA
    with tab_plantilla:
        st.subheader("👥 Plantilla Oficial - C.F. Ginesta Cadet F11")
        st.markdown("Fitxes individuals, partits jugats i titularitats de cada jugadora.")
        st.markdown("---")

        cols = st.columns(2)
        for i, jugadora in enumerate(golejadores_data):
            rol = jugadora.get('rol', 'Jugadora')
            grogues_val = jugadora.get('grogues', 0)
            vermelles_val = jugadora.get('vermelles', 0)
            dorsal_val = jugadora.get('dorsal', '-')
            nom_jugadora = jugadora.get('nom', '').upper()
            titularitats_val = jugadora.get('titularitats', 0)
            partits_jugats_val = jugadora.get('partits_jugats', 0)
            
            if rol == "Portera":
                gols_encaixats_val = jugadora.get('gols_encaixats', 0)
                estat_text = f"🧤 Encaixats: <b>{gols_encaixats_val}</b>"
            else:
                gols_realitzats_val = jugadora.get('gols', 0)
                estat_text = f"⚽ Gols: <b>{gols_realitzats_val}</b>"

            with cols[i % 2]:
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: white; padding: 15px; border-radius: 12px; border-left: 6px solid #5c2d73; margin-bottom: 10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.06);">
                        <div style="font-size: 18px; font-weight: 900; color: #5c2d73; text-transform: uppercase;">
                            #{dorsal_val} — {nom_jugadora} <span style="font-size: 11px; background-color: #f7f5fa; padding: 2px 6px; border-radius: 4px; color: #333; border: 1px solid #ddd;">{rol}</span>
                        </div>
                        <div style="font-size: 13px; color: #1a1a1a; margin-top: 6px; font-weight: 600;">
                            {estat_text} &nbsp;|&nbsp; 🟨 <b>{grogues_val}</b> &nbsp;|&nbsp; 🟥 <b>{vermelles_val}</b>
                        </div>
                        <hr style="margin: 8px 0; border: none; border-top: 1px solid #eee;">
                        <div style="font-size: 11px; color: #1a1a1a;">
                            ⚽ Partits Jugats: <b>{partits_jugats_val}</b> &nbsp;|&nbsp; ⭐ Titularitats: <b>{titularitats_val}</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

    # PESTANYA 4: ESTADÍSTIQUES
    with tab_stats:
        st.subheader("📊 Resum i Estadístiques de l'Equip")
        trams_llista = ["0'-10'", "10'-20'", "20'-30'", "30'-40'", "40'-50'", "50'-60'", "60'-70'", "70'-80'"]
        trams_data_db = []
        try:
            res_trams = supabase.table("trams_gols").select("*").execute()
            trams_data_db = res_trams.data
        except:
            pass

        dict_trams = {t: {"gols_favor": 0, "gols_contra": 0} for t in trams_llista}
        for item in trams_data_db:
            t = item.get("tram")
            if t in dict_trams:
                dict_trams[t]["gols_favor"] = item.get("gols_favor", 0)
                dict_trams[t]["gols_contra"] = item.get("gols_contra", 0)

        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        with col_m1:
            st.metric(label="Partits Jugats", value=n_partits)
        with col_m2:
            st.metric(label="Gols Favor", value=g_favor_total)
        with col_m3:
            st.metric(label="Gols Contra", value=gols_contra_total)
        with col_m4:
            st.metric(label="Porteries Zero", value=porteries_zero)
        with col_m5:
            st.metric(label="Targetes", value=f"🟨{total_grogues}|🟥{total_vermelles}")

        st.markdown("---")

        st.markdown("### 🧤 Rendiment de Porteria (Clean Sheets)")
        col_porteria, _ = st.columns([1, 1])
        with col_porteria:
            partits_amb_gols = max(0, n_partits - porteries_zero)
            fig_clean_sheets = px.pie(
                names=["Porteries a Zero", "Partits amb Gols Encaixats"],
                values=[porteries_zero, partits_amb_gols],
                hole=0.6,
                color_discrete_sequence=["#5c2d73", "#d7bde2"]
            )
            fig_clean_sheets.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#1a1a1a", size=13),
                legend=dict(font=dict(color="#1a1a1a")),
                margin=dict(t=0, b=0, l=0, r=0), 
                height=220
            )
            st.plotly_chart(fig_clean_sheets, use_container_width=True)

        st.markdown("---")

        st.markdown("### ⏱️ Distribució de Gols per Minuts")
        df_trams = pd.DataFrame([
            {"Minuts": t, "Gols Favor": d["gols_favor"], "Gols Contra": d["gols_contra"]}
            for t, d in dict_trams.items()
        ])

        col_gols_favor, col_gols_contra = st.columns(2)
        with col_gols_favor:
            st.markdown("##### ⚽ Gols a Favor")
            fig_favor = px.area(
                df_trams, 
                x="Minuts", 
                y="Gols Favor", 
                color_discrete_sequence=["#5c2d73"]
            )
            fig_favor.update_traces(
                line=dict(width=3, color='#5c2d73'),
                fillcolor='rgba(92, 45, 115, 0.25)',
                mode='lines+markers'
            )
            fig_favor.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#1a1a1a", size=12),
                margin=dict(t=25, b=0, l=0, r=0), 
                height=240,
                xaxis=dict(
                    tickfont=dict(color="#1a1a1a", size=11, weight="bold"),
                    title=dict(font=dict(color="#1a1a1a"))
                ),
                yaxis=dict(
                    showgrid=True, 
                    gridcolor='#e0d8e8',
                    tickfont=dict(color="#1a1a1a", size=11, weight="bold"),
                    title=dict(font=dict(color="#1a1a1a"))
                )
            )
            st.plotly_chart(fig_favor, use_container_width=True)

        with col_gols_contra:
            st.markdown("##### 🛡️ Gols en Contra")
            fig_contra = px.area(
                df_trams, 
                x="Minuts", 
                y="Gols Contra", 
                color_discrete_sequence=["#a569bd"]
            )
            fig_contra.update_traces(
                line=dict(width=3, color='#a569bd'),
                fillcolor='rgba(165, 105, 189, 0.25)',
                mode='lines+markers'
            )
            fig_contra.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#1a1a1a", size=12),
                margin=dict(t=25, b=0, l=0, r=0), 
                height=240,
                xaxis=dict(
                    tickfont=dict(color="#1a1a1a", size=11, weight="bold"),
                    title=dict(font=dict(color="#1a1a1a"))
                ),
                yaxis=dict(
                    showgrid=True, 
                    gridcolor='#e0d8e8',
                    tickfont=dict(color="#1a1a1a", size=11, weight="bold"),
                    title=dict(font=dict(color="#1a1a1a"))
                )
            )
            st.plotly_chart(fig_contra, use_container_width=True)

    # PESTANYA 5: ADMIN
    if st.session_state["auth_level"] == "admin":
        with tab_admin:
            st.subheader("⚙️ Panell d'Administració")
            tab_adm_partits, tab_adm_calendari, tab_adm_stats, tab_adm_trams = st.tabs(["🎬 Vídeos & Fotos", "📅 Calendari", "📊 Mètriques & Jugadores", "⏱️ Trams"])

            with tab_adm_partits:
                st.markdown("#### 🎬 Gestió de Partits, Trams i Targetes")
                sub_p_nou, sub_p_edit = st.tabs(["➕ Pujar Partit Nou (amb Trams i Targetes)", "✏️ Editar / Esborrar Partit Existent"])

                with sub_p_nou:
                    nou_titol = st.text_input("Títol del Partit", key="t_nou")
                    nova_jornada = st.text_input("Jornada (Ex: 1, 2, etc.)", value="1", key="j_nou")
                    nova_data = st.date_input("Data", key="d_nou")
                    nom_rival = st.text_input("Nom Rival", key="r_nou")
                    resultat_partit = st.text_input("Resultat Final (Ex: 3-1)", key="res_nou")
                    condicio_lloc = st.selectbox("Lloc", ["Casa", "Fora"], key="ll_nou")
                    
                    arxiu_escut = st.file_uploader("Escut Rival (PNG)", type=["png", "jpg"], key="esc_vid")
                    arxius_fotos = st.file_uploader("📸 Fotos de Celebració (Màxim 5)", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="fotos_multiples")
                    nou_video_url = st.text_input("Enllaç Vídeo", key="v_url_nou")
                    
                    st.markdown("---")
                    st.markdown("##### ⏱️ Registrar Gols per Trams en aquest Partit")
                    trams_llista = ["0'-10'", "10'-20'", "20'-30'", "30'-40'", "40'-50'", "50'-60'", "60'-70'", "70'-80'"]
                    trams_gols_nous_fav = {}
                    trams_gols_nous_con = {}
                    
                    col_t1, col_t2 = st.columns(2)
                    with col_t1:
                        st.markdown("**⚽ Gols a Favor per Tram**")
                        for t in trams_llista:
                            trams_gols_nous_fav[t] = st.number_input(f"Favor {t}", min_value=0, value=0, key=f"nou_fav_{t}")
                    with col_t2:
                        st.markdown("**🛡️ Gols en Contra per Tram**")
                        for t in trams_llista:
                            trams_gols_nous_con[t] = st.number_input(f"Contra {t}", min_value=0, value=0, key=f"nou_con_{t}")

                    st.markdown("---")
                    st.markdown("##### 🟨 Registrar Targetes en aquest Partit")
                    noms_llista_jugadores = [str(j.get('nom', '')) for j in golejadores_data if j.get('nom')]
                    
                    if "targetes_partit_nou" not in st.session_state:
                        st.session_state["targetes_partit_nou"] = []

                    c_tarj_1, c_tarj_2, c_tarj_3 = st.columns([2, 1, 1])
                    with c_tarj_1:
                        jugadora_card = st.selectbox("Jugadora amonestada", noms_llista_jugadores, key="sel_j_card_nou")
                    with c_tarj_2:
                        minut_card = st.number_input("Minut", min_value=1, max_value=90, value=45, key="num_min_card_nou")
                    with c_tarj_3:
                        tipus_card = st.selectbox("Tipus", ["Groga", "Vermella"], key="sel_tip_card_nou")

                    if st.button("➕ Afegir Targeta a la llista del partit", key="btn_add_card_list"):
                        if jugadora_card:
                            st.session_state["targetes_partit_nou"].append({"jugadora": str(jugadora_card), "minut": int(minut_card), "tipus": str(tipus_card)})
                            st.success(f"Afegida: {jugadora_card} (Minut {minut_card} - {tipus_card})")
                        else:
                            st.warning("⚠️ Selecciona una jugadora vàlida.")

                    if st.session_state["targetes_partit_nou"]:
                        st.write("Targetes registrades per a aquest partit:")
                        for idx, card in enumerate(st.session_state["targetes_partit_nou"]):
                            st.write(f"- **{card.get('jugadora', '')}** | Minut {card.get('minut', '')} | {card.get('tipus', '')}")
                        if st.button("Netejar llista de targetes", key="btnClearCards"):
                            st.session_state["targetes_partit_nou"] = []
                            st.rerun()

                    if st.button("Guardar Partit i Actualitzar Estadístiques"):
                        if nou_titol and nou_video_url:
                            try:
                                escut_path_saved = ""
                                if arxiu_escut is not None:
                                    escut_path_saved = os.path.join("escuts", arxiu_escut.name)
                                    with open(escut_path_saved, "wb") as f:
                                        f.write(arxiu_escut.getbuffer())

                                rutes_fotos = []
                                if arxius_fotos:
                                    for foto in arxius_fotos[:5]:
                                        f_path = os.path.join("fotos_partits", foto.name)
                                        with open(f_path, "wb") as f:
                                            f.write(foto.getbuffer())
                                        rutes_fotos.append(f_path)

                                llista_text_targetes = []
                                comptador_grogues_partit = {}

                                for card in st.session_state["targetes_partit_nou"]:
                                    j_nom = card["jugadora"]
                                    t_tipus = card["tipus"]
                                    minut_card = card["minut"]

                                    res_j = supabase.table("golejadores").select("*").eq("nom", j_nom).execute()
                                    if res_j.data:
                                        j_data = res_j.data[0]
                                        grogues_actuals = int(j_data.get("grogues", 0) or 0)
                                        vermelles_actuals = int(j_data.get("vermelles", 0) or 0)

                                        if j_nom not in comptador_grogues_partit:
                                            comptador_grogues_partit[j_nom] = 0

                                        if t_tipus == "Groga":
                                            grogues_actuals += 1
                                            comptador_grogues_partit[j_nom] += 1
                                            llista_text_targetes.append(f"{j_nom} (Min {minut_card} - Groga)")

                                            if (grogues_actuals % 2 == 0 or comptador_grogues_partit[j_nom] >= 2) and vermelles_actuals == 0:
                                                vermelles_actuals = 1
                                                llista_text_targetes.append(f"{j_nom} (Min {minut_card} - Vermella per doble groga)")
                                        
                                        elif t_tipus == "Vermella":
                                            if vermelles_actuals == 0:
                                                vermelles_actuals = 1
                                            llista_text_targetes.append(f"{j_nom} (Min {minut_card} - Vermella)")

                                        supabase.table("golejadores").update({
                                            "grogues": grogues_actuals,
                                            "vermelles": vermelles_actuals
                                        }).eq("nom", j_nom).execute()

                                text_targetes_guardar = ", ".join(llista_text_targetes) if llista_text_targetes else ""

                                supabase.table("partits").insert({
                                    "titol": nou_titol,
                                    "jornada": nova_jornada.strip(),
                                    "data": str(nova_data),
                                    "rival": nom_rival,
                                    "resultat": resultat_partit,
                                    "lloc": condicio_lloc,
                                    "escut_rival_url": escut_path_saved,
                                    "fotos_partit_urls": ",".join(rutes_fotos),
                                    "video_url": nou_video_url,
                                    "targetes_partit": text_targetes_guardar
                                }).execute()

                                for t in trams_llista:
                                    if trams_gols_nous_fav[t] > 0 or trams_gols_nous_con[t] > 0:
                                        res_t = supabase.table("trams_gols").select("*").eq("tram", t).execute()
                                        ant_fav, ant_con = 0, 0
                                        if res_t.data:
                                            ant_fav = res_t.data[0].get("gols_favor", 0)
                                            ant_con = res_t.data[0].get("gols_contra", 0)
                                        
                                        supabase.table("trams_gols").upsert({
                                            "tram": t,
                                            "gols_favor": ant_fav + trams_gols_nous_fav[t],
                                            "gols_contra": ant_con + trams_gols_nous_con[t]
                                        }, on_conflict="tram").execute()

                                st.session_state["targetes_partit_nou"] = []
                                st.success("🎉 Partit guardat i estadístiques actualitzades automàticament!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")

                with sub_p_edit:
                    partits_existents = []
                    try:
                        res_p = supabase.table("partits").select("*").order("data", desc=True).execute()
                        partits_existents = res_p.data
                    except:
                        pass

                    if not partits_existents:
                        st.warning("No hi ha partits per editar.")
                    else:
                        dict_edit_partits = {}
                        for p in partits_existents:
                            jornada_val = p.get('jornada')
                            j_str = f"J.{jornada_val}" if jornada_val and str(jornada_val).strip() else "J-"
                            titol_val = p.get('titol', 'Partit')
                            res_val = p.get('resultat')
                            res_str = str(res_val) if res_val and str(res_val).strip().lower() != "none" else "vs"
                            dict_edit_partits[f"{j_str} - {titol_val} ({res_str})"] = p

                        sel_partit_str = st.selectbox("Selecciona el partit a modificar/esborrar:", list(dict_edit_partits.keys()), key="sel_ed_p")
                        p_edit = dict_edit_partits[sel_partit_str]

                        val_jornada_text = str(p_edit.get('jornada') or "1")
                        edit_id = p_edit.get('id')
                        edit_titol = st.text_input("Títol", value=p_edit.get('titol', ''), key="ed_t")
                        edit_jornada = st.text_input("Jornada", value=val_jornada_text, key="ed_j")
                        edit_rival = st.text_input("Rival", value=p_edit.get('rival', ''), key="ed_r")
                        edit_resultat = st.text_input("Resultat", value=p_edit.get('resultat', ''), key="ed_res")
                        edit_lloc = st.selectbox("Lloc", ["Casa", "Fora"], index=0 if p_edit.get('lloc', 'Casa')=='Casa' else 1, key="ed_ll")
                        edit_video = st.text_input("Enllaç Vídeo", value=p_edit.get('video_url', ''), key="ed_v")
                        
                        edit_arxiu_escut = st.file_uploader("Canviar Escut Rival", type=["png", "jpg"], key="ed_esc")
                        edit_arxius_fotos = st.file_uploader("Afegir/Canviar Fotos de Celebració (Màxim 5)", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="ed_fotos")
                        esborrar_fotos_check = st.checkbox("🗑️ Esborrar totes les fotos d'aquest partit", key="chk_del_fotos")

                        if st.button("Actualitzar Partit"):
                            try:
                                update_data = {
                                    "titol": edit_titol,
                                    "jornada": edit_jornada.strip(),
                                    "rival": edit_rival,
                                    "resultat": edit_resultat,
                                    "lloc": edit_lloc,
                                    "video_url": edit_video
                                }
                                if edit_arxiu_escut is not None:
                                    escut_path_saved = os.path.join("escuts", edit_arxiu_escut.name)
                                    with open(escut_path_saved, "wb") as f:
                                        f.write(edit_arxiu_escut.getbuffer())
                                    update_data["escut_rival_url"] = escut_path_saved

                                if esborrar_fotos_check:
                                    update_data["fotos_partit_urls"] = ""
                                elif edit_arxius_fotos:
                                    rutes_fotos = []
                                    for foto in edit_arxius_fotos[:5]:
                                        f_path = os.path.join("fotos_partits", foto.name)
                                        with open(f_path, "wb") as f:
                                            f.write(foto.getbuffer())
                                        rutes_fotos.append(f_path)
                                    update_data["fotos_partit_urls"] = ",".join(rutes_fotos)

                                supabase.table("partits").update(update_data).eq("id", edit_id).execute()

                                st.success("✅ Partit actualitzat correctament!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al actualitzar: {e}")

                        st.markdown("---")
                        st.markdown("##### 🗑️ Zona de Perill (Esborrar Partit Sencer)")
                        confirm_key_p = f"confirm_del_partit_{edit_id}"
                        if confirm_key_p not in st.session_state:
                            st.session_state[confirm_key_p] = False

                        if not st.session_state[confirm_key_p]:
                            if st.button("🗑️ Eliminar aquest partit completament", type="secondary", key="btn_init_del_p"):
                                st.session_state[confirm_key_p] = True
                                st.rerun()
                        else:
                            st.warning(f"⚠️ Estàs segur que vols eliminar permanentment el partit **{edit_titol}**?")
                            col_dp1, col_dp2 = st.columns(2)
                            with col_dp1:
                                if st.button("Sí, eliminar partit", type="primary", key="btn_confirm_del_p"):
                                    try:
                                        supabase.table("partits").delete().eq("id", edit_id).execute()
                                        st.session_state[confirm_key_p] = False
                                        st.success("🗑️ Partit eliminat.")
                                        time.sleep(1)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error al eliminar: {e}")
                            with col_dp2:
                                if st.button("Cancel·lar", key="btn_cancel_del_p"):
                                    st.session_state[confirm_key_p] = False
                                    st.rerun()

            # PESTANYA ADMIN: CALENDARI UNIFICAT
            with tab_adm_calendari:
                st.markdown("#### 📅 Gestió Unificada del Calendari Oficial")
                st.markdown("Selecciona una jornada de la 1a volta (1-13) per editar **l'anada i la tornada a la vegada**, o tria **'➕ Afegir nova jornada'**.")

                cal_existents = []
                try:
                    res_c_ed = supabase.table("calendari").select("*").execute()
                    cal_existents = sorted(res_c_ed.data, key=lambda x: int(x.get('jornada', 1) or 1))
                except:
                    pass

                opcions_calendari = ["➕ Afegir nova jornada (Anada + Tornada Automàtica)"]
                dict_map_cal = {}
                for c in cal_existents:
                    j_val = c.get('jornada', 1)
                    r_val = c.get('rival', 'Rival')
                    d_val = c.get('data', '')
                    voltag = " (Anada)" if int(j_val) <= 13 else " (Tornada)"
                    txt = f"Jornada {j_val} vs {r_val} ({d_val}){voltag}"
                    opcions_calendari.append(txt)
                    dict_map_cal[txt] = c

                sel_accio_cal = st.selectbox("Selecciona opció o partit:", opcions_calendari, key="sel_unificat_calendari")

                st.markdown("---")

                if sel_accio_cal == "➕ Afegir nova jornada (Anada + Tornada Automàtica)":
                    st.markdown("##### ➕ Creació de Nova Jornada (Anada i Tornada)")
                    st.markdown("Introdueix els partits de la **1a volta (Jornades 1 a 13)**. El programa crearà automàticament la tornada, l'escut i l'adreça de casa.")

                    cal_jornada = st.number_input("Jornada (1 a 13)", min_value=1, max_value=13, value=1, key="cj_nou")
                    cal_rival = st.text_input("Rival", key="cr_nou")
                    cal_lloc = st.selectbox("Lloc a l'anada", ["Casa", "Fora"], key="cl_nou")
                    cal_escut = st.file_uploader("Escut del Rival (PNG)", type=["png", "jpg"], key="escut_cal_nou")

                    st.markdown("---")
                    st.markdown("🟢 **Partit d'Anada:**")
                    cal_data = st.date_input("Data de l'anada", key="cd_nou")
                    cal_hora = st.text_input("Hora de l'anada", value="10:30", key="ch_nou")
                    
                    default_maps_anada = DIRECCIO_CASA if cal_lloc == "Casa" else ""
                    cal_maps = st.text_input("Google Maps de l'estadi de l'anada", value=default_maps_anada, key="cmaps_nou")

                    st.markdown("🔵 **Partit de Tornada (Segona Volta):**")
                    cal_data_volta = st.date_input("Data de la tornada", key="cd_volta_nou")
                    cal_hora_volta = st.text_input("Hora de la tornada", value="10:30", key="ch_volta_nou")
                    
                    lloc_tornada_preview = "Fora" if cal_lloc == "Casa" else "Casa"
                    default_maps_volta = DIRECCIO_CASA if lloc_tornada_preview == "Casa" else ""
                    cal_maps_volta = st.text_input("Google Maps de l'estadi de la tornada", value=default_maps_volta, key="cmaps_volta_nou")

                    if st.button("Guardar Nova Jornada (Anada i Tornada)"):
                        if cal_rival:
                            try:
                                escut_cal_path = ""
                                if cal_escut is not None:
                                    escut_path = os.path.join("escuts", cal_escut.name)
                                    with open(escut_path, "wb") as f:
                                        f.write(cal_escut.getbuffer())
                                    escut_cal_path = escut_path

                                maps_anada_final = DIRECCIO_CASA if cal_lloc == "Casa" else cal_maps.strip()

                                supabase.table("calendari").upsert({
                                    "id": int(time.time()),
                                    "jornada": int(cal_jornada),
                                    "data": str(cal_data),
                                    "hora": cal_hora,
                                    "rival": cal_rival,
                                    "lloc": cal_lloc,
                                    "escut_rival_url": escut_cal_path,
                                    "maps_url": maps_anada_final,
                                    "resultat": ""
                                }, on_conflict="jornada").execute()

                                jornada_tornada = int(cal_jornada) + 13
                                lloc_tornada = "Fora" if cal_lloc == "Casa" else "Casa"
                                maps_tornada_final = DIRECCIO_CASA if lloc_tornada == "Casa" else cal_maps_volta.strip()

                                supabase.table("calendari").upsert({
                                    "id": int(time.time()) + 1,
                                    "jornada": int(jornada_tornada),
                                    "data": str(cal_data_volta),
                                    "hora": cal_hora_volta,
                                    "rival": cal_rival,
                                    "lloc": lloc_tornada,
                                    "escut_rival_url": escut_cal_path,
                                    "maps_url": maps_tornada_final,
                                    "resultat": ""
                                }, on_conflict="jornada").execute()

                                st.success(f"✅ Jornada {cal_jornada} (Anada) i Jornada {jornada_tornada} (Tornada) afegides correctament amb l'escut i mapes sincronitzats!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")

                else:
                    partit_carregat = dict_map_cal[sel_accio_cal]
                    c_id = partit_carregat.get("id")
                    jornada_actual_num = int(partit_carregat.get("jornada", 1))

                    if jornada_actual_num <= 13:
                        jornada_tornada_num = jornada_actual_num + 13
                        partit_tornada_obj = next((item for item in cal_existents if int(item.get("jornada", 0)) == jornada_tornada_num), None)

                        st.markdown(f"##### ✏️ Editant Jornada {jornada_actual_num} (Anada) i Jornada {jornada_tornada_num} (Tornada)")

                        escut_actual_a = partit_carregat.get("escut_rival_url", "")
                        if escut_actual_a and os.path.exists(escut_actual_a):
                            st.image(escut_actual_a, width=40)
                            st.caption("Escut actual del rival (es sincronitzarà automàticament a la tornada)")

                        edit_arxiu_escut_nou = st.file_uploader("Canviar Escut del Rival (Opcional)", type=["png", "jpg"], key=f"up_esc_{c_id}")

                        st.markdown("🟢 **Partit d'Anada:**")
                        edit_r_anada = st.text_input("Rival (Anada)", value=partit_carregat.get("rival", ""), key=f"ec_r_a_{c_id}")
                        
                        d_str_a = partit_carregat.get("data", str(datetime.date.today()))
                        try:
                            d_obj_a = datetime.datetime.strptime(d_str_a, "%Y-%m-%d").date()
                        except:
                            d_obj_a = datetime.date.today()
                        edit_d_anada = st.date_input("Data anada", value=d_obj_a, key=f"ec_d_a_{c_id}")
                        edit_h_anada = st.text_input("Hora anada", value=partit_carregat.get("hora", ""), key=f"ec_h_a_{c_id}")
                        
                        lloc_a_ant = partit_carregat.get("lloc", "Casa")
                        idx_la = 0 if lloc_a_ant == "Casa" else 1
                        edit_lloc_a = st.selectbox("Lloc anada", ["Casa", "Fora"], index=idx_la, key=f"ec_ll_a_{c_id}")
                        edit_res_a = st.text_input("Resultat anada", value=partit_carregat.get("resultat", ""), key=f"ec_res_a_{c_id}")
                        
                        default_edit_maps_a = DIRECCIO_CASA if edit_lloc_a == "Casa" else partit_carregat.get("maps_url", "")
                        edit_maps_a = st.text_input("Google Maps anada", value=default_edit_maps_a, key=f"ec_maps_a_{c_id}")

                        st.markdown("---")
                        st.markdown(f"🔵 **Partit de Tornada (Jornada {jornada_tornada_num}):**")
                        
                        t_id = partit_tornada_obj.get("id") if partit_tornada_obj else int(time.time()) + 99
                        d_str_t = partit_tornada_obj.get("data", str(datetime.date.today())) if partit_tornada_obj else str(datetime.date.today())
                        try:
                            d_obj_t = datetime.datetime.strptime(d_str_t, "%Y-%m-%d").date()
                        except:
                            d_obj_t = datetime.date.today()

                        edit_d_tornada = st.date_input("Data tornada", value=d_obj_t, key=f"ec_d_t_{t_id}")
                        edit_h_tornada = st.text_input("Hora tornada", value=partit_tornada_obj.get("hora", "10:30") if partit_tornada_obj else "10:30", key=f"ec_h_t_{t_id}")
                        
                        lloc_t_ant = partit_tornada_obj.get("lloc", ("Fora" if lloc_a_ant == "Casa" else "Casa")) if partit_tornada_obj else ("Fora" if lloc_a_ant == "Casa" else "Casa")
                        idx_lt = 0 if lloc_t_ant == "Casa" else 1
                        edit_lloc_t = st.selectbox("Lloc tornada", ["Casa", "Fora"], index=idx_lt, key=f"ec_ll_t_{t_id}")
                        edit_res_t = st.text_input("Resultat tornada", value=partit_tornada_obj.get("resultat", "") if partit_tornada_obj else "", key=f"ec_res_t_{t_id}")
                        
                        default_edit_maps_t = DIRECCIO_CASA if edit_lloc_t == "Casa" else (partit_tornada_obj.get("maps_url", "") if partit_tornada_obj else "")
                        edit_maps_t = st.text_input("Google Maps tornada", value=default_edit_maps_t, key=f"ec_maps_t_{t_id}")

                        col_act1, col_act2 = st.columns(2)
                        with col_act1:
                            if st.button("💾 Guardar Canvis (Anada i Tornada)", key=f"btn_save_both_{c_id}"):
                                try:
                                    escut_final_path = escut_actual_a
                                    if edit_arxiu_escut_nou is not None:
                                        escut_final_path = os.path.join("escuts", edit_arxiu_escut_nou.name)
                                        with open(escut_final_path, "wb") as f:
                                            f.write(edit_arxiu_escut_nou.getbuffer())

                                    maps_anada_final = DIRECCIO_CASA if edit_lloc_a == "Casa" else edit_maps_a.strip()
                                    maps_tornada_final = DIRECCIO_CASA if edit_lloc_t == "Casa" else edit_maps_t.strip()

                                    supabase.table("calendari").update({
                                        "jornada": int(jornada_actual_num),
                                        "rival": edit_r_anada,
                                        "data": str(edit_d_anada),
                                        "hora": edit_h_anada,
                                        "lloc": edit_lloc_a,
                                        "escut_rival_url": escut_final_path,
                                        "resultat": edit_res_a.strip(),
                                        "maps_url": maps_anada_final
                                    }).eq("id", c_id).execute()

                                    supabase.table("calendari").upsert({
                                        "id": t_id,
                                        "jornada": int(jornada_tornada_num),
                                        "rival": edit_r_anada,
                                        "data": str(edit_d_tornada),
                                        "hora": edit_h_tornada,
                                        "lloc": edit_lloc_t,
                                        "escut_rival_url": escut_final_path,
                                        "resultat": edit_res_t.strip(),
                                        "maps_url": maps_tornada_final
                                    }, on_conflict="jornada").execute()

                                    st.success("✅ Canvis guardats correctament (Anada i Tornada amb escut i mapes sincronitzats)!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")

                        with col_act2:
                            if st.button("🗑️ Eliminar Jornada Sencera", key=f"btn_del_both_{c_id}"):
                                try:
                                    supabase.table("calendari").delete().eq("jornada", int(jornada_actual_num)).execute()
                                    supabase.table("calendari").delete().eq("jornada", int(jornada_tornada_num)).execute()
                                    st.success("🗑️ Jornades eliminades.")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")

                    else:
                        st.markdown(f"##### ✏️ Editant Partit de Tornada - Jornada {jornada_actual_num}")

                        edit_c_jornada = st.number_input("Jornada", min_value=14, max_value=26, value=jornada_actual_num, key=f"ec_j_{c_id}")
                        edit_c_rival = st.text_input("Rival", value=partit_carregat.get("rival", ""), key=f"ec_r_{c_id}")
                        
                        data_str_ant = partit_carregat.get("data", str(datetime.date.today()))
                        try:
                            data_obj_ant = datetime.datetime.strptime(data_str_ant, "%Y-%m-%d").date()
                        except:
                            data_obj_ant = datetime.date.today()

                        edit_c_data = st.date_input("Data del Partit", value=data_obj_ant, key=f"ec_d_{c_id}")
                        edit_c_hora = st.text_input("Hora", value=partit_carregat.get("hora", ""), key=f"ec_h_{c_id}")
                        
                        lloc_actual = partit_carregat.get("lloc", "Casa")
                        idx_lloc = 0 if lloc_actual == "Casa" else 1
                        edit_c_lloc = st.selectbox("Lloc", ["Casa", "Fora"], index=idx_lloc, key=f"ec_ll_{c_id}")
                        
                        edit_c_resultat = st.text_input("Resultat Final (Ex: 3-1)", value=partit_carregat.get("resultat", ""), key=f"ec_res_{c_id}")
                        
                        default_edit_maps_single = DIRECCIO_CASA if edit_c_lloc == "Casa" else partit_carregat.get("maps_url", "")
                        edit_c_maps = st.text_input("Enllaç Google Maps (Estadi)", value=default_edit_maps_single, key=f"ec_maps_{c_id}")

                        col_act1, col_act2 = st.columns(2)
                        with col_act1:
                            if st.button("💾 Guardar Canvis de la Tornada", key=f"btn_save_{c_id}"):
                                try:
                                    maps_final_single = DIRECCIO_CASA if edit_c_lloc == "Casa" else edit_c_maps.strip()
                                    supabase.table("calendari").update({
                                        "jornada": int(edit_c_jornada),
                                        "rival": edit_c_rival,
                                        "data": str(edit_c_data),
                                        "hora": edit_c_hora,
                                        "lloc": edit_c_lloc,
                                        "resultat": edit_c_resultat.strip(),
                                        "maps_url": maps_final_single
                                    }).eq("id", c_id).execute()
                                    st.success("✅ Partit de tornada actualitzat correctament!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")

                        with col_act2:
                            if st.button("🗑️️ Eliminar Partit", key=f"btn_del_{c_id}"):
                                try:
                                    supabase.table("calendari").delete().eq("id", c_id).execute()
                                    st.success("🗑️ Partit eliminat del calendari.")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")

            # PESTANYA ADMIN: ESTADÍSTIQUES I MÈTRIQUES
            with tab_adm_stats:
                st.markdown("#### 📈 Mètriques Generals")
                with st.form("form_metriques"):
                    p_jugats = st.number_input("Partits Jugats", min_value=0, value=n_partits)
                    p_zero = st.number_input("Porteries a Zero", min_value=0, value=porteries_zero)
                    g_propia = st.number_input("Gols Pròpia Porta", min_value=0, value=gols_propia_porta)
                    g_contra_input = st.number_input("Total Gols Contra", min_value=0, value=gols_contra_total)
                    
                    if st.form_submit_button("Actualitzar Mètriques"):
                        sincronitzar_estadistiques_generals(p_jugats, p_zero, g_propia, g_contra_input)
                        st.success("✅ Mètriques actualitzades!")
                        st.rerun()

                st.markdown("---")
                st.markdown("#### ⚽ Gestió de Jugadores (Afegir, Gols, Targetes, Partits i Titularitats)")
                noms_jugadores = [f"#{int(j.get('dorsal', 0) or 0)} - {j.get('nom').upper()}" for j in golejadores_data]
                noms_jugadores.append("➕ Afegir nova jugadora...")
                
                jugadora_seleccionada_str = st.selectbox("Selecciona una jugadora:", noms_jugadores)
                
                if jugadora_seleccionada_str == "➕ Afegir nova jugadora...":
                    nova_jugadora_nom = st.text_input("Nom de la nova jugadora:")
                    nou_dorsal = st.number_input("Dorsal:", min_value=1, max_value=99, value=12)
                    nou_rol = st.selectbox("Rol al camp:", ["Jugadora", "Portera"])
                    gols_inicials = st.number_input("Gols inicials:", min_value=0, value=0)
                    grogues_inicials = st.number_input("Targetes grogues:", min_value=0, value=0)
                    vermelles_inicials = st.number_input("Targetes vermelles (màx 1):", min_value=0, max_value=1, value=0)
                    gols_encaixats_inicials = st.number_input("Gols encaixats (si portera):", min_value=0, value=0)
                    partits_jugats_inicials = st.number_input("Partits jugats inicials:", min_value=0, value=0)
                    titularitats_inicials = st.number_input("Titularitats inicials:", min_value=0, value=0)
                    
                    if st.button("Crear Jugadora"):
                        if nova_jugadora_nom:
                            try:
                                supabase.table("golejadores").upsert({
                                    "nom": nova_jugadora_nom.strip(),
                                    "dorsal": int(nou_dorsal),
                                    "gols": int(gols_inicials),
                                    "rol": nou_rol,
                                    "grogues": int(grogues_inicials),
                                    "vermelles": min(1, int(vermelles_inicials)),
                                    "gols_encaixats": int(gols_encaixats_inicials),
                                    "partits_jugats": int(partits_jugats_inicials),
                                    "titularitats": int(titularitats_inicials)
                                }, on_conflict="nom").execute()
                                
                                sincronitzar_estadistiques_generals(n_partits, porteries_zero, gols_propia_porta, gols_contra_total)
                                st.success(f"🎉 Jugadora {nova_jugadora_nom.upper()} afegida!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                else:
                    jugadora_seleccionada = jugadora_seleccionada_str.split(" - ")[1]
                    j_actual = next((j for j in golejadores_data if j.get('nom').upper() == jugadora_seleccionada), {})
                    
                    dorsal_actual = int(j_actual.get('dorsal', 0) or 0)
                    gols_actuals = int(j_actual.get('gols', 0) or 0)
                    rol_actual = j_actual.get('rol', 'Jugadora')
                    grogues_actuals = int(j_actual.get('grogues', 0) or 0)
                    vermelles_actuals = int(j_actual.get('vermelles', 0) or 0)
                    gols_encaixats_actuals = int(j_actual.get('gols_encaixats', 0) or 0)
                    partits_jugats_actuals = int(j_actual.get('partits_jugats', 0) or 0)
                    titularitats_actuals = int(j_actual.get('titularitats', 0) or 0)
                    nom_real = j_actual.get('nom', jugadora_seleccionada)
                    
                    st.info(f"Dorsal: **#{dorsal_actual}** | **{nom_real.upper()}** ({rol_actual})")
                    
                    c_ed1, c_ed2 = st.columns(2)
                    with c_ed1:
                        nou_dorsal_input = st.number_input("Modificar Dorsal:", min_value=1, max_value=99, value=dorsal_actual if dorsal_actual > 0 else 1)
                    with c_ed2:
                        nou_canvi_rol = st.selectbox("Modificar Rol:", ["Jugadora", "Portera"], index=0 if rol_actual=="Jugadora" else 1, key="canvi_rol_sel")

                    c_ed3, c_ed4 = st.columns(2)
                    with c_ed3:
                        nous_partits_jugats = st.number_input("Modificar Partits Jugats:", min_value=0, value=partits_jugats_actuals)
                    with c_ed4:
                        noves_titularitats = st.number_input("Modificar Titularitats:", min_value=0, value=titularitats_actuals)

                    if st.button("Actualitzar Dades de la Jugadora"):
                        try:
                            supabase.table("golejadores").upsert({
                                "nom": nom_real,
                                "dorsal": int(nou_dorsal_input),
                                "gols": gols_actuals,
                                "rol": nou_canvi_rol,
                                "grogues": grogues_actuals,
                                "vermelles": vermelles_actuals,
                                "gols_encaixats": gols_encaixats_actuals,
                                "partits_jugats": int(nous_partits_jugats),
                                "titularitats": int(noves_titularitats)
                            }, on_conflict="nom").execute()
                            st.success("✅ Dades actualitzades correctament!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

                    st.markdown("##### Sumar / Restar Gols, Targetes, Partits i Titularitats")
                    if rol_actual == "Portera":
                        c_bt1, c_bt2, c_bt3 = st.columns(3)
                        with c_bt1:
                            if st.button("➕ Sumar Gol Encaixat"):
                                try:
                                    supabase.table("golejadores").upsert({
                                        "nom": nom_real, "dorsal": dorsal_actual, "gols": gols_actuals, "rol": rol_actual,
                                        "grogues": grogues_actuals, "vermelles": vermelles_actuals,
                                        "gols_encaixats": gols_encaixats_actuals + 1, "partits_jugats": partits_jugats_actuals, "titularitats": titularitats_actuals
                                    }, on_conflict="nom").execute()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")
                            if st.button("➖ Restar Gol Encaixat") and gols_encaixats_actuals > 0:
                                try:
                                    supabase.table("golejadores").upsert({
                                        "nom": nom_real, "dorsal": dorsal_actual, "gols": gols_actuals, "rol": rol_actual,
                                        "grogues": grogues_actuals, "vermelles": vermelles_actuals,
                                        "gols_encaixats": gols_encaixats_actuals - 1, "partits_jugats": partits_jugats_actuals, "titularitats": titularitats_actuals
                                    }, on_conflict="nom").execute()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")
                    else:
                        c_bt1, c_bt2, c_bt3 = st.columns(3)
                        with c_bt1:
                            if st.button("➕ Sumar 1 Gol"):
                                try:
                                    supabase.table("golejadores").upsert({
                                        "nom": nom_real, "dorsal": dorsal_actual, "gols": gols_actuals + 1, "rol": rol_actual,
                                        "grogues": grogues_actuals, "vermelles": vermelles_actuals,
                                        "gols_encaixats": gols_encaixats_actuals, "partits_jugats": partits_jugats_actuals, "titularitats": titularitats_actuals
                                    }, on_conflict="nom").execute()
                                    sincronitzar_estadistiques_generals(n_partits, porteries_zero, gols_propia_porta, gols_contra_total)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")
                            if st.button("➖ Restar 1 Gol") and gols_actuals > 0:
                                try:
                                    supabase.table("golejadores").upsert({
                                        "nom": nom_real, "dorsal": dorsal_actual, "gols": gols_actuals - 1, "rol": rol_actual,
                                        "grogues": grogues_actuals, "vermelles": vermelles_actuals,
                                        "gols_encaixats": gols_encaixats_actuals, "partits_jugats": partits_jugats_actuals, "titularitats": titularitats_actuals
                                    }, on_conflict="nom").execute()
                                    sincronitzar_estadistiques_generals(n_partits, porteries_zero, gols_propia_porta, gols_contra_total)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")

                    with c_bt2:
                        if st.button("🟨 Sumar Groga"):
                            try:
                                nova_g = grogues_actuals + 1
                                nova_v = vermelles_actuals
                                if nova_g % 2 == 0 and nova_v == 0:
                                    nova_v = 1
                                supabase.table("golejadores").upsert({
                                    "nom": nom_real, "dorsal": dorsal_actual, "gols": gols_actuals, "rol": rol_actual,
                                    "grogues": nova_g, "vermelles": nova_v,
                                    "gols_encaixats": gols_encaixats_actuals, "partits_jugats": partits_jugats_actuals, "titularitats": titularitats_actuals
                                }, on_conflict="nom").execute()
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                        if st.button("➖ Restar Groga") and grogues_actuals > 0:
                            try:
                                supabase.table("golejadores").upsert({
                                    "nom": nom_real, "dorsal": dorsal_actual, "gols": gols_actuals, "rol": rol_actual,
                                    "grogues": grogues_actuals - 1, "vermelles": vermelles_actuals,
                                    "gols_encaixats": gols_encaixats_actuals, "partits_jugats": partits_jugats_actuals, "titularitats": titularitats_actuals
                                }, on_conflict="nom").execute()
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")

                    with c_bt3:
                        if st.button("🟥 Sumar Vermella") and vermelles_actuals == 0:
                            try:
                                supabase.table("golejadores").upsert({
                                    "nom": nom_real, "dorsal": dorsal_actual, "gols": gols_actuals, "rol": rol_actual,
                                    "grogues": grogues_actuals, "vermelles": 1,
                                    "gols_encaixats": gols_encaixats_actuals, "partits_jugats": partits_jugats_actuals, "titularitats": titularitats_actuals
                                }, on_conflict="nom").execute()
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                        if st.button("➖ Restar Vermella") and vermelles_actuals > 0:
                            try:
                                supabase.table("golejadores").upsert({
                                    "nom": nom_real, "dorsal": dorsal_actual, "gols": gols_actuals, "rol": rol_actual,
                                    "grogues": grogues_actuals, "vermelles": 0,
                                    "gols_encaixats": gols_encaixats_actuals, "partits_jugats": partits_jugats_actuals, "titularitats": titularitats_actuals
                                }, on_conflict="nom").execute()
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")

                    st.markdown("---")
                    st.markdown("##### 🗑️ Zona de Perill (Eliminar Jugadora)")
                    confirm_key = f"confirm_del_{nom_real}"
                    if confirm_key not in st.session_state:
                        st.session_state[confirm_key] = False

                    if not st.session_state[confirm_key]:
                        if st.button(f"🗑️ Eliminar a {nom_real}", type="secondary"):
                            st.session_state[confirm_key] = True
                            st.rerun()
                    else:
                        st.warning(f"⚠️ Estàs segur que vols eliminar permanentment a **{nom_real}**?")
                        col_del1, col_del2 = st.columns(2)
                        with col_del1:
                            if st.button("Sí, eliminar", type="primary"):
                                try:
                                    supabase.table("golejadores").delete().eq("nom", nom_real).execute()
                                    sincronitzar_estadistiques_generals(n_partits, porteries_zero, gols_propia_porta, gols_contra_total)
                                    st.session_state[confirm_key] = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")
                        with col_del2:
                            if st.button("Cancel·lar"):
                                st.session_state[confirm_key] = False
                                st.rerun()

            # PESTANYA ADMIN: TRAMS
            with tab_adm_trams:
                st.markdown("#### ⏱️ Actualització Ràpida de Gols per Minuts (+ / -)")
                tram_coll = st.selectbox("Selecciona el bloc de minuts a modificar:", trams_llista, key="select_tram_minuts")
                actual_fav = dict_trams[tram_coll]["gols_favor"]
                actual_con = dict_trams[tram_coll]["gols_contra"]
                
                st.info(f"📊 **Bloc seleccionat: Minuts {tram_coll}** — Gols a Favor: **{actual_fav}** ⚽ | Gols en Contra: **{actual_con}** 🛡️")
                
                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    if st.button(f"➕ Sumar Favor ({tram_coll})", key="btn_sum_fav"):
                        try:
                            supabase.table("trams_gols").upsert({
                                "tram": tram_coll, "gols_favor": actual_fav + 1, "gols_contra": actual_con
                            }, on_conflict="tram").execute()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                with c_f2:
                    if st.button(f"➖ Restar Favor ({tram_coll})", key="btn_res_fav") and actual_fav > 0:
                        try:
                            supabase.table("trams_gols").upsert({
                                "tram": tram_coll, "gols_favor": actual_fav - 1, "gols_contra": actual_con
                            }, on_conflict="tram").execute()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

                st.markdown("---")
                c_c1, c_c2 = st.columns(2)
                with c_c1:
                    if st.button(f"➕ Sumar Contra ({tram_coll})", key="btn_sum_con"):
                        try:
                            supabase.table("trams_gols").upsert({
                                "tram": tram_coll, "gols_favor": actual_fav, "gols_contra": actual_con + 1
                            }, on_conflict="tram").execute()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                with c_c2:
                    if st.button(f"➖ Restar Contra ({tram_coll})", key="btn_res_con") and actual_con > 0:
                        try:
                            supabase.table("trams_gols").upsert({
                                "tram": tram_coll, "gols_favor": actual_fav, "gols_contra": actual_con - 1
                            }, on_conflict="tram").execute()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

if check_access():
    main()
