import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
import os
import time

# --- CONFIGURACIÓ DE LA PÀGINA ---
st.set_page_config(
    page_title="Videoteca & Estadístiques - C.F. Ginesta",
    page_icon="https://files.fcf.cat/escudos/clubes/escudos/00100_0001239324_GINESTA.png",
    layout="wide"
)

LOGO_URL = "https://files.fcf.cat/escudos/clubes/escudos/00100_0001239324_GINESTA.png"

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

# --- ESTIL I COLORS CORPORATIUS (OPTIMITZAT PER A MÒBIL) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f7f5fa;
        color: #2b1b3d;
    }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #2b1b3d !important;
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
        color: #2b1b3d !important;
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
        color: #2b1b3d !important;
    }
    div[data-baseweb="popover"] div[role="option"] * {
        color: #2b1b3d !important;
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
    col1, col2 = st.columns([1, 4])
    with col1:
        try:
            st.image(LOGO_URL, width=70)
        except:
            st.write("⚽")
    with col2:
        st.title("C.F. Ginesta - Cadet F11")
        st.markdown("*Videoteca & Estadístiques*")

    st.divider()

    golejadores_data = []
    try:
        res_gol = supabase.table("golejadores").select("*").order("dorsal", desc=False).execute()
        golejadores_data = res_gol.data
    except:
        pass

    if not golejadores_data:
        golejadores_data = [
            {"nom": "Clàudia", "dorsal": 10, "gols": 8, "rol": "Jugadora", "grogues": 1, "vermelles": 0, "gols_encaixats": 0},
            {"nom": "Júlia", "dorsal": 7, "gols": 6, "rol": "Jugadora", "grogues": 0, "vermelles": 0, "gols_encaixats": 0},
            {"nom": "Martina", "dorsal": 8, "gols": 5, "rol": "Jugadora", "grogues": 2, "vermelles": 0, "gols_encaixats": 0},
            {"nom": "Berta", "dorsal": 11, "gols": 4, "rol": "Jugadora", "grogues": 0, "vermelles": 0, "gols_encaixats": 0},
            {"nom": "Carla", "dorsal": 14, "gols": 4, "rol": "Jugadora", "grogues": 1, "vermelles": 0, "gols_encaixats": 0},
            {"nom": "Aina", "dorsal": 6, "gols": 3, "rol": "Jugadora", "grogues": 0, "vermelles": 0, "gols_encaixats": 0},
            {"nom": "Noa", "dorsal": 1, "gols": 0, "rol": "Portera", "grogues": 0, "vermelles": 0, "gols_encaixats": 5}
        ]

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
            st.error(f"❌ Error: {e}")

    if st.session_state["auth_level"] == "admin":
        tab_videos, tab_calendari, tab_stats, tab_admin = st.tabs(["🎬 Videoteca", "📅 Calendari", "📊 Estadístiques", "⚙️ Admin"])
    else:
        tab_videos, tab_calendari, tab_stats = st.tabs(["🎬 Videoteca", "📅 Calendari", "📊 Estadístiques"])

    # PESTANYA 1: VÍDEOS I GALERIA DE FOTOS
    with tab_videos:
        st.subheader("📺 Partits Gravats, Resultats i Galeria")
        partits = []
        try:
            response = supabase.table("partits").select("*").order("data", desc=True).execute()
            partits = response.data
        except Exception as e:
            st.error(f"❌ Error: {e}")

        if not partits:
            st.warning("Encara no hi ha partits registrats.")
        else:
            opcions_partits = {f"J.{p.get('jornada', '')} - {p.get('titol', 'Partit')} ({p.get('resultat', 'vs')})": p for p in partits}
            partit_seleccionat_str = st.selectbox("Selecciona un partit:", list(opcions_partits.keys()))
            partit_actual = opcions_partits[partit_seleccionat_str]
            
            rival = partit_actual.get('rival', 'Rival')
            resultat = partit_actual.get('resultat', ' - ')
            lloc = partit_actual.get('lloc', 'Casa')
            escut_path = partit_actual.get('escut_rival_url') 
            fotos_str = partit_actual.get('fotos_partit_urls', '')
            
            st.markdown("---")
            col_res1, col_res2, col_res3 = st.columns([2, 3, 2])
            
            if lloc == "Fora":
                with col_res1:
                    c_r1, c_r2 = st.columns([2, 1])
                    with c_r1:
                        st.markdown(f"<h4 style='text-align: right; color: #5c2d73; margin-top: 5px; font-size: 14px;'>{rival}</h4>", unsafe_allow_html=True)
                    with c_r2:
                        if escut_path and os.path.exists(escut_path):
                            st.image(escut_path, width=35)
                        else:
                            st.write("🛡️")
                with col_res2:
                    st.markdown(f"<h2 style='text-align: center; color: #2b1b3d; margin: 0; font-size: 18px;'>{resultat}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-size: 11px; color: #666;'>({lloc})</p>", unsafe_allow_html=True)
                with col_res3:
                    c_g1, c_g2 = st.columns([1, 2])
                    with c_g1:
                        st.image(LOGO_URL, width=35)
                    with c_g2:
                        st.markdown(f"<h4 style='color: #5c2d73; margin-top: 5px; font-size: 14px;'>C.F. Ginesta</h4>", unsafe_allow_html=True)
            else:
                with col_res1:
                    c_g1, c_g2 = st.columns([1, 2])
                    with c_g1:
                        st.image(LOGO_URL, width=35)
                    with c_g2:
                        st.markdown(f"<h4 style='color: #5c2d73; margin-top: 5px; font-size: 14px;'>C.F. Ginesta</h4>", unsafe_allow_html=True)
                with col_res2:
                    st.markdown(f"<h2 style='text-align: center; color: #2b1b3d; margin: 0; font-size: 18px;'>{resultat}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-size: 11px; color: #666;'>({lloc})</p>", unsafe_allow_html=True)
                with col_res3:
                    c_r1, c_r2 = st.columns([2, 1])
                    with c_r1:
                        st.markdown(f"<h4 style='text-align: right; color: #5c2d73; margin-top: 5px; font-size: 14px;'>{rival}</h4>", unsafe_allow_html=True)
                    with c_r2:
                        if escut_path and os.path.exists(escut_path):
                            st.image(escut_path, width=35)
                        else:
                            st.write("🛡️")

            st.markdown(f"### 🏟️ {partit_actual.get('titol')}")
            st.markdown(f"📅 **Data:** {partit_actual.get('data')} &nbsp;|&nbsp; 🏆 **Jornada:** {partit_actual.get('jornada')}")
            
            # Reproductors de vídeo protegits contra FileNotFoundError
            video_url = partit_actual.get('video_url') or partit_actual.get('enllaç_video')
            if video_url and isinstance(video_url, str) and (video_url.startswith("http://") or video_url.startswith("https://")):
                try:
                    st.video(video_url)
                except Exception:
                    st.warning("⚠️ No s'ha pogut carregar el reproductor amb aquest enllaç.")
            else:
                st.warning("⚠️ L'enllaç del vídeo d'aquest partit no és vàlid o no està disponible.")

            if fotos_str:
                lletres_fotos = [f.strip() for f in fotos_str.split(",") if f.strip()]
                if lletres_fotos:
                    st.markdown("---")
                    st.markdown("### 📸 Galeria de Fotos del Partit")
                    for f_path in lletres_fotos:
                        if os.path.exists(f_path):
                            st.image(f_path, use_container_width=True)

    # PESTANYA 2: CALENDARI
    with tab_calendari:
        st.subheader("📅 Calendari Oficial")
        calendari_data = []
        try:
            res_cal = supabase.table("calendari").select("*").order("jornada", desc=False).execute()
            calendari_data = res_cal.data
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

                color_bg_lloc = "#5c2d73" if lloc == "Casa" else "#a569bd"

                with st.container():
                    st.markdown(f"""
                        <div style="background-color: white; padding: 10px 12px; border-radius: 10px; border: 1px solid #e0d8e8; margin-bottom: 8px; box-shadow: 1px 1px 4px rgba(0,0,0,0.03);">
                            <div style="font-size: 11px; color: #5c2d73; font-weight: bold; margin-bottom: 6px; border-bottom: 1px solid #f0e8f5; padding-bottom: 4px;">
                                Jornada {jornada} &nbsp;|&nbsp; 📅 {data} &nbsp;|&nbsp; ⏰ {hora}
                            </div>
                    """, unsafe_allow_html=True)

                    col_left, col_vs, col_right = st.columns([3, 1, 3])
                    
                    if lloc == "Fora":
                        with col_left:
                            cr1, cr2 = st.columns([1, 3])
                            with cr1:
                                if escut_path and os.path.exists(escut_path):
                                    st.image(escut_path, width=28)
                                else:
                                    st.write("🛡️")
                            with cr2:
                                st.markdown(f"<p style='margin-top: 4px; font-weight: bold; font-size: 11px; color: #2b1b3d;'>{rival}</p>", unsafe_allow_html=True)
                        
                        with col_vs:
                            st.markdown(f"""
                                <div style="text-align: center; padding-top: 2px;">
                                    <span style="color: white; background-color: {color_bg_lloc}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;">{lloc}</span>
                                </div>
                            """, unsafe_allow_html=True)

                        with col_right:
                            cg1, cg2 = st.columns([3, 1])
                            with cg1:
                                st.markdown("<p style='text-align: right; margin-top: 4px; font-weight: bold; font-size: 11px; color: #2b1b3d;'>C.F. Ginesta</p>", unsafe_allow_html=True)
                            with cg2:
                                st.image(LOGO_URL, width=28)
                    else:
                        with col_left:
                            cg1, cg2 = st.columns([1, 3])
                            with cg1:
                                st.image(LOGO_URL, width=28)
                            with cg2:
                                st.markdown(f"<p style='margin-top: 4px; font-weight: bold; font-size: 11px; color: #2b1b3d;'>C.F. Ginesta</p>", unsafe_allow_html=True)
                        
                        with col_vs:
                            st.markdown(f"""
                                <div style="text-align: center; padding-top: 2px;">
                                    <span style="color: white; background-color: {color_bg_lloc}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;">{lloc}</span>
                                </div>
                            """, unsafe_allow_html=True)

                        with col_right:
                            cr1, cr2 = st.columns([3, 1])
                            with cr1:
                                st.markdown(f"<p style='text-align: right; margin-top: 4px; font-weight: bold; font-size: 11px; color: #2b1b3d;'>{rival}</p>", unsafe_allow_html=True)
                            with cr2:
                                if escut_path and os.path.exists(escut_path):
                                    st.image(escut_path, width=28)
                                else:
                                    st.write("🛡️")

                    st.markdown("</div>", unsafe_allow_html=True)

    # PESTANYA 3: ESTADÍSTIQUES
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
            st.metric(label="Partits", value=n_partits)
        with col_m2:
            st.metric(label="Favor", value=g_favor_total)
        with col_m3:
            st.metric(label="Contra", value=gols_contra_total)
        with col_m4:
            st.metric(label="P. Zero", value=porteries_zero)
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
                font=dict(color="#2b1b3d", size=13),
                legend=dict(font=dict(color="#2b1b3d")),
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
            fig_favor = px.bar(df_trams, x="Minuts", y="Gols Favor", color_discrete_sequence=["#5c2d73"])
            fig_favor.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#2b1b3d", size=11),
                margin=dict(t=10, b=0, l=0, r=0), 
                height=220
            )
            st.plotly_chart(fig_favor, use_container_width=True)

        with col_gols_contra:
            st.markdown("##### 🛡️ Gols en Contra")
            fig_contra = px.bar(df_trams, x="Minuts", y="Gols Contra", color_discrete_sequence=["#a569bd"])
            fig_contra.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#2b1b3d", size=11),
                margin=dict(t=10, b=0, l=0, r=0), 
                height=220
            )
            st.plotly_chart(fig_contra, use_container_width=True)

        st.markdown("---")
        st.markdown("### ⚽ Plantilla Oficial - C.F. Ginesta")
        
        cols = st.columns(2)
        for i, jugadora in enumerate(golejadores_data):
            rol = jugadora.get('rol', 'Jugadora')
            grogues_val = jugadora.get('grogues', 0)
            vermelles_val = jugadora.get('vermelles', 0)
            dorsal_val = jugadora.get('dorsal', '-')
            nom_jugadora = jugadora.get('nom', '').upper()
            
            if rol == "Portera":
                gols_encaixats_val = jugadora.get('gols_encaixats', 0)
                estat_text = f"🧤 Encaixats: <b>{gols_encaixats_val}</b>"
            else:
                gols_realitzats_val = jugadora.get('gols', 0)
                estat_text = f"⚽ Gols: <b>{gols_realitzats_val}</b>"
            
            with cols[i % 2]:
                st.markdown(f"""
                    <div style="background-color: white; padding: 12px; border-radius: 10px; border-left: 4px solid #5c2d73; margin-bottom: 10px; box-shadow: 1px 1px 6px rgba(0,0,0,0.04);">
                        <div style="display: flex; align-items: center; margin-bottom: 8px;">
                            <div style="background-color: #f7f5fa; border: 2px solid #5c2d73; color: #5c2d73; border-radius: 6px; width: 40px; height: 40px; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-right: 10px; flex-shrink: 0;">
                                <span style="font-weight: 800; font-size: 16px; line-height: 1;">{dorsal_val}</span>
                                <span style="font-size: 6px; color: #666; font-weight: 700; text-transform: uppercase;">{rol}</span>
                            </div>
                            <div style="flex-grow: 1; overflow: hidden;">
                                <h4 style="margin: 0; color: #5c2d73; font-size: 15px; font-weight: 900; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{nom_jugadora}</h4>
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f0e8f5; padding-top: 6px; font-size: 11px; color: #2b1b3d;">
                            <div>{estat_text}</div>
                            <div>🟨<b>{grogues_val}</b> 🟥<b>{vermelles_val}</b></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # PESTANYA 4: ADMIN
    if st.session_state["auth_level"] == "admin":
        with tab_admin:
            st.subheader("⚙️ Panell d'Administració")
            tab_adm_partits, tab_adm_calendari, tab_adm_stats, tab_adm_trams = st.tabs(["🎬 Vídeos & Fotos", "📅 Calendari", "📊 Mètriques & Jugadores", "⏱️ Trams"])

            with tab_adm_partits:
                st.markdown("#### ➕ Pujar Partit, Vídeo i Fins a 5 Fotos")
                nou_titol = st.text_input("Títol del Partit")
                nova_jornada = st.number_input("Jornada", min_value=1, max_value=38, value=1)
                nova_data = st.date_input("Data")
                nom_rival = st.text_input("Nom Rival")
                resultat_partit = st.text_input("Resultat Final (Ex: 3-1)")
                condicio_lloc = st.selectbox("Lloc", ["Casa", "Fora"])
                
                arxiu_escut = st.file_uploader("Escut Rival (PNG)", type=["png", "jpg"], key="esc_vid")
                arxius_fotos = st.file_uploader("📸 Fotos de Celebració (Màxim 5)", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="fotos_multiples")
                nou_video_url = st.text_input("Enllaç Vídeo (URL web)")
                
                if st.button("Guardar Partit"):
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

                            supabase.table("partits").insert({
                                "titol": nou_titol,
                                "jornada": int(nova_jornada),
                                "data": str(nova_data),
                                "rival": nom_rival,
                                "resultat": resultat_partit,
                                "lloc": condicio_lloc,
                                "escut_rival_url": escut_path_saved,
                                "fotos_partit_urls": ",".join(rutes_fotos),
                                "video_url": nou_video_url
                            }).execute()
                            st.success("🎉 Partit guardat amb vídeo i galeria de fotos!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

            with tab_adm_calendari:
                st.markdown("#### 📅 Afegir Calendari")
                cal_jornada = st.number_input("Jornada", min_value=1, max_value=38, value=1, key="cj")
                cal_data = st.date_input("Data", key="cd")
                cal_hora = st.text_input("Hora", value="10:30")
                cal_rival = st.text_input("Rival", key="cr")
                cal_lloc = st.selectbox("Lloc", ["Casa", "Fora"], key="cl")
                cal_escut = st.file_uploader("Escut del Rival per al Calendari (PNG)", type=["png", "jpg"], key="escut_cal")
                
                if st.button("Afegir al Calendari"):
                    if cal_rival:
                        try:
                            escut_cal_path = ""
                            if cal_escut is not None:
                                escut_cal_path = os.path.join("escuts", cal_escut.name)
                                with open(escut_cal_path, "wb") as f:
                                    f.write(cal_escut.getbuffer())

                            supabase.table("calendari").insert({
                                "id": int(time.time()),
                                "jornada": int(cal_jornada),
                                "data": str(cal_data),
                                "hora": cal_hora,
                                "rival": cal_rival,
                                "lloc": cal_lloc,
                                "escut_rival_url": escut_cal_path
                            }).execute()
                            st.success("✅ Partit afegit al calendari!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

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
                st.markdown("#### ⚽ Gestió de Jugadores (Dorsal, Rol, Gols, Targetes, Eliminar)")
                noms_jugadores = [f"#{int(j.get('dorsal', 0) or 0)} - {j.get('nom').upper()}" for j in golejadores_data]
                noms_jugadores.append("➕ Afegir nova jugadora...")
                
                jugadora_seleccionada_str = st.selectbox("Selecciona una jugadora:", noms_jugadores)
                
                if jugadora_seleccionada_str == "➕ Afegir nova jugadora...":
                    nova_jugadora_nom = st.text_input("Nom de la nova jugadora:")
                    nou_dorsal = st.number_input("Dorsal:", min_value=1, max_value=99, value=12)
                    nou_rol = st.selectbox("Rol al camp:", ["Jugadora", "Portera"])
                    gols_inicials = st.number_input("Gols inicials:", min_value=0, value=0)
                    grogues_inicials = st.number_input("Targetes grogues inicials:", min_value=0, value=0)
                    vermelles_inicials = st.number_input("Targetes vermelles inicials:", min_value=0, value=0)
                    gols_encaixats_inicials = st.number_input("Gols encaixats inicials (si és portera):", min_value=0, value=0)
                    
                    if st.button("Crear Jugadora"):
                        if nova_jugadora_nom:
                            try:
                                supabase.table("golejadores").upsert({
                                    "nom": nova_jugadora_nom.strip(),
                                    "dorsal": int(nou_dorsal),
                                    "gols": int(gols_inicials),
                                    "rol": nou_rol,
                                    "grogues": int(grogues_inicials),
                                    "vermelles": int(vermelles_inicials),
                                    "gols_encaixats": int(gols_encaixats_inicials)
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
                    nom_real = j_actual.get('nom', jugadora_seleccionada)
                    
                    st.info(f"Dorsal: **#{dorsal_actual}** | Jugadora: **{nom_real.upper()}** | Rol: **{rol_actual}** | Gols: **{gols_actuals}** | Grogues: **{grogues_actuals}** | Vermelles: **{vermelles_actuals}**")
                    
                    c_ed1, c_ed2 = st.columns(2)
                    with c_ed1:
                        nou_dorsal_input = st.number_input("Modificar Dorsal:", min_value=1, max_value=99, value=dorsal_actual if dorsal_actual > 0 else 1)
                    with c_ed2:
                        nou_canvi_rol = st.selectbox("Modificar Rol:", ["Jugadora", "Portera"], index=0 if rol_actual=="Jugadora" else 1, key="canvi_rol_sel")
                    
                    if nou_dorsal_input != dorsal_actual or nou_canvi_rol != rol_actual:
                        if st.button("Actualitzar Dades Bàsiques"):
                            try:
                                supabase.table("golejadores").upsert({
                                    "nom": nom_real,
                                    "dorsal": int(nou_dorsal_input),
                                    "gols": gols_actuals,
                                    "rol": nou_canvi_rol,
                                    "grogues": grogues_actuals,
                                    "vermelles": vermelles_actuals,
                                    "gols_encaixats": gols_encaixats_actuals
                                }, on_conflict="nom").execute()
                                st.success("Dades actualitzades!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")

                    st.markdown("##### Sumar / Restar Gols i Targetes")
                    
                    if rol_actual == "Portera":
                        c_bt1, c_bt2, c_bt3 = st.columns(3)
                        with c_bt1:
                            if st.button("➕ Sumar Gol Encaixat"):
                                try:
                                    supabase.table("golejadores").upsert({
                                        "nom": nom_real,
                                        "dorsal": dorsal_actual,
                                        "gols": gols_actuals,
                                        "rol": rol_actual,
                                        "grogues": grogues_actuals,
                                        "vermelles": vermelles_actuals,
                                        "gols_encaixats": gols_encaixats_actuals + 1
                                    }, on_conflict="nom").execute()
                                    st.success("Gol encaixat sumat!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")
                            if st.button("➖ Restar Gol Encaixat") and gols_encaixats_actuals > 0:
                                try:
                                    supabase.table("golejadores").upsert({
                                        "nom": nom_real,
                                        "dorsal": dorsal_actual,
                                        "gols": gols_actuals,
                                        "rol": rol_actual,
                                        "grogues": grogues_actuals,
                                        "vermelles": vermelles_actuals,
                                        "gols_encaixats": gols_encaixats_actuals - 1
                                    }, on_conflict="nom").execute()
                                    st.success("Gol encaixat restat.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")
                    else:
                        c_bt1, c_bt2, c_bt3 = st.columns(3)
                        with c_bt1:
                            if st.button("➕ Sumar 1 Gol"):
                                try:
                                    supabase.table("golejadores").upsert({
                                        "nom": nom_real,
                                        "dorsal": dorsal_actual,
                                        "gols": gols_actuals + 1,
                                        "rol": rol_actual,
                                        "grogues": grogues_actuals,
                                        "vermelles": vermelles_actuals,
                                        "gols_encaixats": gols_encaixats_actuals
                                    }, on_conflict="nom").execute()
                                    
                                    sincronitzar_estadistiques_generals(n_partits, porteries_zero, gols_propia_porta, gols_contra_total)
                                    st.success("Gol sumat i sincronitzat!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")
                            if st.button("➖ Restar 1 Gol") and gols_actuals > 0:
                                try:
                                    supabase.table("golejadores").upsert({
                                        "nom": nom_real,
                                        "dorsal": dorsal_actual,
                                        "gols": gols_actuals - 1,
                                        "rol": rol_actual,
                                        "grogues": grogues_actuals,
                                        "vermelles": vermelles_actuals,
                                        "gols_encaixats": gols_encaixats_actuals
                                    }, on_conflict="nom").execute()
                                    
                                    sincronitzar_estadistiques_generals(n_partits, porteries_zero, gols_propia_porta, gols_contra_total)
                                    st.success("Gol restat i sincronitzat.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")

                    with c_bt2:
                        if st.button("🟨 Sumar Groga"):
                            try:
                                supabase.table("golejadores").upsert({
                                    "nom": nom_real,
                                    "dorsal": dorsal_actual,
                                    "gols": gols_actuals,
                                    "rol": rol_actual,
                                    "grogues": grogues_actuals + 1,
                                    "vermelles": vermelles_actuals,
                                    "gols_encaixats": gols_encaixats_actuals
                                }, on_conflict="nom").execute()
                                st.success("Groga sumada!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                        if st.button("➖ Restar Groga") and grogues_actuals > 0:
                            try:
                                supabase.table("golejadores").upsert({
                                    "nom": nom_real,
                                    "dorsal": dorsal_actual,
                                    "gols": gols_actuals,
                                    "rol": rol_actual,
                                    "grogues": grogues_actuals - 1,
                                    "vermelles": vermelles_actuals,
                                    "gols_encaixats": gols_encaixats_actuals
                                }, on_conflict="nom").execute()
                                st.success("Groga restada.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")

                    with c_bt3:
                        if st.button("🟥 Sumar Vermella"):
                            try:
                                supabase.table("golejadores").upsert({
                                    "nom": nom_real,
                                    "dorsal": dorsal_actual,
                                    "gols": gols_actuals,
                                    "rol": rol_actual,
                                    "grogues": grogues_actuals,
                                    "vermelles": vermelles_actuals + 1,
                                    "gols_encaixats": gols_encaixats_actuals
                                }, on_conflict="nom").execute()
                                st.success("Vermella sumada!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                        if st.button("➖ Restar Vermella") and vermelles_actuals > 0:
                            try:
                                supabase.table("golejadores").upsert({
                                    "nom": nom_real,
                                    "dorsal": dorsal_actual,
                                    "gols": gols_actuals,
                                    "rol": rol_actual,
                                    "grogues": grogues_actuals,
                                    "vermelles": vermelles_actuals - 1,
                                    "gols_encaixats": gols_encaixats_actuals
                                }, on_conflict="nom").execute()
                                st.success("Vermella restada.")
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
                                    st.success(f"🗑️ S'ha eliminat a {nom_real}.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")
                        with col_del2:
                            if st.button("Cancel·lar"):
                                st.session_state[confirm_key] = False
                                st.rerun()

            with tab_adm_trams:
                st.markdown("#### ⏱️ Actualització Ràpida de Gols per Minuts (+ / -)")
                tram_coll = st.selectbox("Selecciona el bloc de minuts a modificar:", trams_llista, key="select_tram_minuts")
                actual_fav = dict_trams[tram_coll]["gols_favor"]
                actual_con = dict_trams[tram_coll]["gols_contra"]
                
                st.info(f"📊 **Bloc seleccionat: Minuts {tram_coll}** — Gols a Favor: **{actual_fav}** ⚽ | Gols en Contra: **{actual_con}** 🛡️")
                
                st.markdown("##### ⚽ Gols a Favor (Marcats en aquest tram)")
                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    if st.button(f"➕ Sumar Favor ({tram_coll})", key="btn_sum_fav"):
                        try:
                            supabase.table("trams_gols").upsert({
                                "tram": tram_coll,
                                "gols_favor": actual_fav + 1,
                                "gols_contra": actual_con
                            }, on_conflict="tram").execute()
                            st.success(f"Gol a favor sumat al bloc {tram_coll}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                with c_f2:
                    if st.button(f"➖ Restar Favor ({tram_coll})", key="btn_res_fav") and actual_fav > 0:
                        try:
                            supabase.table("trams_gols").upsert({
                                "tram": tram_coll,
                                "gols_favor": actual_fav - 1,
                                "gols_contra": actual_con
                            }, on_conflict="tram").execute()
                            st.success(f"Gol a favor restat al bloc {tram_coll}.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

                st.markdown("---")
                st.markdown("##### 🛡️ Gols en Contra (Encaixats en aquest tram)")
                c_c1, c_c2 = st.columns(2)
                with c_c1:
                    if st.button(f"➕ Sumar Contra ({tram_coll})", key="btn_sum_con"):
                        try:
                            supabase.table("trams_gols").upsert({
                                "tram": tram_coll,
                                "gols_favor": actual_fav,
                                "gols_contra": actual_con + 1
                            }, on_conflict="tram").execute()
                            st.success(f"Gol en contra sumat al bloc {tram_coll}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                with c_c2:
                    if st.button(f"➖ Restar Contra ({tram_coll})", key="btn_res_con") and actual_con > 0:
                        try:
                            supabase.table("trams_gols").upsert({
                                "tram": tram_coll,
                                "gols_favor": actual_fav,
                                "gols_contra": actual_con - 1
                            }, on_conflict="tram").execute()
                            st.success(f"Gol en contra restat.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

if check_access():
    main()
