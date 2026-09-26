import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
import os
import time

# --- CONFIGURACIÓ DE LA PÀGINA ---
st.set_page_config(
    page_title="Videoteca & Estadístiques - C.F. Ginesta",
    page_icon="⚽",
    layout="wide"
)

# --- ESTIL I COLORS PERSONALITZATS ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f7f5fa;
        color: #2b1b3d;
    }
    h1, h2, h3, h4, h5, h6, p, label {
        color: #2b1b3d !important;
    }
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
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: white !important;
        color: #2b1b3d !important;
        border: 2px solid #5c2d73 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #5c2d73 !important;
        color: white !important;
        border-color: #4a2858 !important;
        border-radius: 8px;
    }
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

# Assegurar carpeta d'escuts
if not os.path.exists("escuts"):
    os.makedirs("escuts")

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
            if input_pass == "admin2026":
                st.session_state["auth_level"] = "admin"
                st.rerun()
            elif input_pass == "ginesta2026":
                st.session_state["auth_level"] = "family"
                st.rerun()
            else:
                st.error("❌ Contrasenya incorrecta. Torna-ho a provar.")
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
            st.image("logo.png", width=100)
        except:
            st.write("⚽")
    with col2:
        st.title("C.F. Ginesta - Cadet F11")
        st.markdown("*Videoteca Oficial & Estadístiques de la Temporada*")

    st.divider()

    # Pestanyes segons el rol
    if st.session_state["auth_level"] == "admin":
        tab_videos, tab_calendari, tab_stats, tab_admin = st.tabs(["🎬 Videoteca", "📅 Calendari", "📊 Estadístiques", "⚙️ Administració"])
    else:
        tab_videos, tab_calendari, tab_stats = st.tabs(["🎬 Videoteca", "📅 Calendari", "📊 Estadístiques"])

    # ==========================================
    # PESTANYA 1: VÍDEOS DELS PARTITS
    # ==========================================
    with tab_videos:
        st.subheader("📺 Partits Gravats i Resultats")
        
        partits = []
        try:
            response = supabase.table("partits").select("*").order("data", desc=True).execute()
            partits = response.data
        except Exception as e:
            st.error(f"❌ Error en carregar els partits: {e}")

        if not partits:
            st.warning("Encara no hi ha partits registrats a la base de dades.")
        else:
            opcions_partits = {f"Jornada {p.get('jornada', '')} - {p.get('titol', 'Partit')} ({p.get('resultat', 'vs')})": p for p in partits}
            
            partit_seleccionat_str = st.selectbox("Selecciona un partit per veure:", list(opcions_partits.keys()))
            partit_actual = opcions_partits[partit_seleccionat_str]
            
            rival = partit_actual.get('rival', 'Rival')
            resultat = partit_actual.get('resultat', ' - ')
            lloc = partit_actual.get('lloc', 'Casa')
            escut_path = partit_actual.get('escut_rival_url') 
            
            st.markdown("---")
            
            col_res1, col_res2, col_res3 = st.columns([2, 3, 2])
            with col_res1:
                c_g1, c_g2 = st.columns([1, 2])
                with c_g1:
                    try:
                        st.image("logo.png", width=45)
                    except:
                        pass
                with c_g2:
                    st.markdown("<h4 style='color: #5c2d73; margin-top: 5px;'>C.F. Ginesta</h4>", unsafe_allow_html=True)
                    
            with col_res2:
                st.markdown(f"<h2 style='text-align: center; color: #2b1b3d; margin: 0;'>{resultat}</h2>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; font-size: 14px; color: #666;'>({lloc})</p>", unsafe_allow_html=True)
                
            with col_res3:
                c_r1, c_r2 = st.columns([2, 1])
                with c_r1:
                    st.markdown(f"<h4 style='text-align: right; color: #5c2d73; margin-top: 5px;'>{rival}</h4>", unsafe_allow_html=True)
                with c_r2:
                    if escut_path and os.path.exists(escut_path):
                        st.image(escut_path, width=45)
                    else:
                        st.write("🛡️")

            st.markdown(f"### 🏟️ {partit_actual.get('titol')}")
            st.markdown(f"📅 **Data:** {partit_actual.get('data')} &nbsp;&nbsp;|&nbsp;&nbsp; 🏆 **Jornada:** {partit_actual.get('jornada')}")
            
            video_url = partit_actual.get('video_url') or partit_actual.get('enllaç_video')
            if video_url:
                st.video(video_url)
            else:
                st.warning("⚠️ El vídeo d'aquest partit encara no està disponible.")

    # ==========================================
    # PESTANYA 2: CALENDARI DE LA TEMPORADA
    # ==========================================
    with tab_calendari:
        st.subheader("📅 Calendari Oficial de la Temporada")
        st.markdown("Consulta els enfrontaments, horaris i si juguem a casa o fora.")
        
        calendari_data = []
        try:
            res_cal = supabase.table("calendari").select("*").order("jornada", desc=False).execute()
            calendari_data = res_cal.data
        except Exception as e:
            st.info("Encara no s'ha creat cap calendari a Supabase.")

        if not calendari_data:
            st.warning("No hi ha partits programats al calendari actualment.")
        else:
            for partit in calendari_data:
                jornada = partit.get('jornada', '-')
                data = partit.get('data', '-')
                hora = partit.get('hora', '-')
                rival = partit.get('rival', '-')
                lloc = partit.get('lloc', 'Casa')
                escut_path = partit.get('escut_rival_url', '')

                # Targeta visual simètrica per cada partit del calendari
                with st.container():
                    st.markdown(f"""
                        <div style="background-color: white; padding: 12px 15px; border-radius: 10px; border: 1px solid #e0d8e8; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.03);">
                            <p style="margin: 0; font-size: 13px; color: #5c2d73; font-weight: bold;">Jornada {jornada} &nbsp;|&nbsp; 📅 {data} &nbsp;|&nbsp; ⏰ {hora}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    col_ginesta, col_vs, col_rival = st.columns([3, 1, 3])
                    
                    # Columna Esquerra: C.F. Ginesta amb el seu logo
                    with col_ginesta:
                        cg1, cg2 = st.columns([1, 3])
                        with cg1:
                            try:
                                st.image("logo.png", width=38)
                            except:
                                st.write("⚽")
                        with cg2:
                            st.markdown("<p style='margin-top: 6px; font-weight: bold; color: #2b1b3d;'>C.F. Ginesta</p>", unsafe_allow_html=True)
                    
                    # Columna Central: Informació de VS i Lloc (Casa / Fora)
                    with col_vs:
                        color_lloc = "#5c2d73" if lloc == "Casa" else "#a569bd"
                        st.markdown(f"""
                            <div style="text-align: center; padding-top: 5px;">
                                <span style="font-size: 14px; font-weight: bold; color: #888;">VS</span><br>
                                <span style="color: white; background-color: {color_lloc}; padding: 2px 8px; border-radius: 5px; font-size: 11px;"><b>{lloc}</b></span>
                            </div>
                        """, unsafe_allow_html=True)

                    # Columna Dreta: Rival amb el seu escut pujat
                    with col_rival:
                        cr1, cr2 = st.columns([3, 1])
                        with cr1:
                            st.markdown(f"<p style='text-align: right; margin-top: 6px; font-weight: bold; color: #2b1b3d;'>{rival}</p>", unsafe_allow_html=True)
                        with cr2:
                            if escut_path and os.path.exists(escut_path):
                                st.image(escut_path, width=38)
                            else:
                                st.write("🛡️")
                st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # PESTANYA 3: ESTADÍSTIQUES I GOLEJADORES
    # ==========================================
    with tab_stats:
        st.subheader("📊 Resum i Estadístiques de l'Equip (2x40 min)")
        
        try:
            res_stats = supabase.table("estadistiques_generals").select("*").execute()
            if res_stats.data:
                st_data = res_stats.data[0]
                n_partits = st_data.get("partits_jugats", 12)
                porteries_zero = st_data.get("porteries_zero", 7)
            else:
                n_partits, porteries_zero = 12, 7
        except:
            n_partits, porteries_zero = 12, 7

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

        g_favor_total = sum(d["gols_favor"] for d in dict_trams.values())
        g_contra_total = sum(d["gols_contra"] for d in dict_trams.values())

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric(label="Partits Jugats", value=n_partits)
        with col_b:
            st.metric(label="Gols a Favor (Total)", value=g_favor_total)
        with col_c:
            st.metric(label="Gols en Contra (Total)", value=g_contra_total)

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
            fig_clean_sheets.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=240)
            st.plotly_chart(fig_clean_sheets, use_container_width=True)

        st.markdown("---")

        st.markdown("### ⏱️ Anàlisi Tàctica per Minuts de Partit (8 blocs de 10 min)")
        
        df_trams = pd.DataFrame([
            {"Minuts": t, "Gols Favor": d["gols_favor"], "Gols Contra": d["gols_contra"]}
            for t, d in dict_trams.items()
        ])

        col_gols_favor, col_gols_contra = st.columns(2)

        with col_gols_favor:
            st.markdown("##### ⚽ Gols a Favor (Marcats)")
            fig_favor = px.bar(df_trams, x="Minuts", y="Gols Favor", color_discrete_sequence=["#5c2d73"])
            fig_favor.update_layout(
                xaxis_title="Minuts del Partit",
                yaxis_title="Gols",
                margin=dict(t=10, b=0, l=0, r=0), 
                height=250
            )
            st.plotly_chart(fig_favor, use_container_width=True)

        with col_gols_contra:
            st.markdown("##### 🛡️ Gols en Contra (Encaixats)")
            fig_contra = px.bar(df_trams, x="Minuts", y="Gols Contra", color_discrete_sequence=["#a569bd"])
            fig_contra.update_layout(
                xaxis_title="Minuts del Partit",
                yaxis_title="Gols",
                margin=dict(t=10, b=0, l=0, r=0), 
                height=250
            )
            st.plotly_chart(fig_contra, use_container_width=True)

        st.markdown("---")

        st.markdown("### ⚽ Golejadores de l'Equip (Llista No Competitiva)")
        
        golejadores_data = []
        try:
            res_gol = supabase.table("golejadores").select("*").order("gols", desc=True).execute()
            golejadores_data = res_gol.data
        except:
            pass

        if not golejadores_data:
            golejadores_data = [
                {"nom": "Clàudia", "gols": 8}, {"nom": "Júlia", "gols": 6},
                {"nom": "Martina", "gols": 5}, {"nom": "Berta", "gols": 4},
                {"nom": "Carla", "gols": 4}, {"nom": "Aina", "gols": 3}, {"nom": "Noa", "gols": 2}
            ]

        cols = st.columns(3)
        for i, jugadora in enumerate(golejadores_data):
            with cols[i % 3]:
                st.markdown(f"""
                    <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 5px solid #5c2d73; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                        <h4 style="margin: 0; color: #5c2d73;">{jugadora.get('nom')}</h4>
                        <p style="margin: 5px 0 0 0; font-size: 16px; color: #2b1b3d !important;">⚽ <b>{jugadora.get('gols')}</b> gols</p>
                    </div>
                """, unsafe_allow_html=True)

    # ==========================================
    # PESTANYA 4: ADMINISTRACIÓ (Només ADMIN)
    # ==========================================
    if st.session_state["auth_level"] == "admin":
        with tab_admin:
            st.subheader("⚙️ Panell d'Administració i Gestió")
            
            tab_adm_partits, tab_adm_calendari, tab_adm_stats, tab_adm_trams = st.tabs(["🎬 Videoteca", "📅 Gestionar Calendari", "📊 Mètriques & Golejadores", "⏱️ Gols per Minuts"])

            # --- SUBPANELL 1: VÍDEOS DE PARTITS ---
            with tab_adm_partits:
                st.markdown("#### ➕ Pujar Vídeo i Resultat de Partit")
                
                nou_titol = st.text_input("Títol del Partit (Ex: C.F. Ginesta vs CE Manresa)")
                nova_jornada = st.number_input("Número de Jornada", min_value=1, max_value=38, value=1)
                nova_data = st.date_input("Data del Partit")
                
                c_r1, c_r2 = st.columns(2)
                with c_r1:
                    nom_rival = st.text_input("Nom de l'Equip Rival")
                with c_r2:
                    resultat_partit = st.text_input("Resultat Final (Ex: 3-1)")
                    
                c_l1, c_l2 = st.columns(2)
                with c_l1:
                    condicio_lloc = st.selectbox("Lloc del Partit", ["Casa", "Fora"])
                with c_l2:
                    arxiu_escut = st.file_uploader("Pujar Escut del Rival (PNG)", type=["png", "jpg", "jpeg"], key="escut_video")

                nou_video_url = st.text_input("Enllaç del Vídeo (YouTube, Drive, etc.)")
                
                if st.button("Guardar Partit a Videoteca"):
                    if nou_titol and nou_video_url:
                        try:
                            escut_path_saved = ""
                            if arxiu_escut is not None:
                                escut_path_saved = os.path.join("escuts", arxiu_escut.name)
                                with open(escut_path_saved, "wb") as f:
                                    f.write(arxiu_escut.getbuffer())

                            supabase.table("partits").insert({
                                "titol": nou_titol,
                                "jornada": int(nova_jornada),
                                "data": str(nova_data),
                                "rival": nom_rival,
                                "resultat": resultat_partit,
                                "lloc": condicio_lloc,
                                "escut_rival_url": escut_path_saved,
                                "video_url": nou_video_url
                            }).execute()
                            st.success("🎉 Partit guardat a la videoteca!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                    else:
                        st.warning("⚠️ Omple almenys el títol i l'enllaç del vídeo.")

            # --- SUBPANELL 2: CREAR CALENDARI (Amb ID automàtic corregit) ---
            with tab_adm_calendari:
                st.markdown("#### 📅 Programar Partit al Calendari Oficial")
                
                cal_jornada = st.number_input("Número de Jornada", min_value=1, max_value=38, value=1, key="cal_j")
                cal_data = st.date_input("Data del Partit", key="cal_d")
                cal_hora = st.text_input("Hora del Partit (Ex: 10:30)", value="10:30")
                
                c_cr1, c_cr2 = st.columns(2)
                with c_cr1:
                    cal_rival = st.text_input("Equip Rival", key="cal_r")
                with c_cr2:
                    cal_lloc = st.selectbox("Lloc", ["Casa", "Fora"], key="cal_l")

                cal_escut = st.file_uploader("Escut del Rival per al Calendari (PNG)", type=["png", "jpg", "jpeg"], key="escut_cal")

                if st.button("Afegir al Calendari"):
                    if cal_rival:
                        try:
                            escut_cal_path = ""
                            if cal_escut is not None:
                                escut_cal_path = os.path.join("escuts", cal_escut.name)
                                with open(escut_cal_path, "wb") as f:
                                    f.write(cal_escut.getbuffer())

                            supabase.table("calendari").insert({
                                "id": int(time.time()),  # Solució de l'ID automàtic
                                "jornada": int(cal_jornada),
                                "data": str(cal_data),
                                "hora": cal_hora,
                                "rival": cal_rival,
                                "lloc": cal_lloc,
                                "escut_rival_url": escut_cal_path
                            }).execute()
                            st.success("✅ Partit afegit correctament al calendari!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                    else:
                        st.warning("⚠️ Introdueix el nom del rival.")

            # --- SUBPANELL 3: MÈTRIQUES I GOLEJADORES ---
            with tab_adm_stats:
                st.markdown("#### 📈 Mètriques Generals")
                with st.form("form_metriques"):
                    col_m1, col_m4 = st.columns(2)
                    with col_m1:
                        p_jugats = st.number_input("Partits Jugats", min_value=0, value=n_partits)
                    with col_m4:
                        p_zero = st.number_input("Porteries a Zero", min_value=0, value=porteries_zero)
                    
                    if st.form_submit_button("Actualitzar Partits i Porteries"):
                        try:
                            supabase.table("estadistiques_generals").delete().neq("id", 0).execute()
                            supabase.table("estadistiques_generals").insert({
                                "partits_jugats": int(p_jugats),
                                "gols_favor": int(g_favor_total),
                                "gols_contra": int(g_contra_total),
                                "porteries_zero": int(p_zero)
                            }).execute()
                            st.success("✅ Mètriques actualitzades!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

                st.markdown("---")
                st.markdown("#### ⚽ Gols de les Jugadores (+ / -)")
                
                noms_jugadores = [j.get('nom') for j in golejadores_data] if golejadores_data else ["Clàudia", "Júlia", "Martina", "Berta", "Carla", "Aina", "Noa"]
                noms_jugadores.append("➕ Afegir nova jugadora...")
                
                jugadora_seleccionada = st.selectbox("Selecciona una jugadora:", noms_jugadores)
                
                if jugadora_seleccionada == "➕ Afegir nova jugadora...":
                    nova_jugadora_nom = st.text_input("Nom de la nova jugadora:")
                    gols_inicials = st.number_input("Gols inicials:", min_value=0, value=0)
                    if st.button("Crear Jugadora"):
                        if nova_jugadora_nom:
                            try:
                                supabase.table("golejadores").upsert({"nom": nova_jugadora_nom.strip(), "gols": int(gols_inicials)}, on_conflict="nom").execute()
                                st.success(f"🎉 Jugadora {nova_jugadora_nom} afegida!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                else:
                    gols_actuals = next((j.get('gols') for j in golejadores_data if j.get('nom') == jugadora_seleccionada), 0)
                    st.info(f"Jugadora: **{jugadora_seleccionada}** - Gols: **{gols_actuals}** ⚽")
                    
                    col_bt1, col_bt2 = st.columns(2)
                    with col_bt1:
                        if st.button("➕ Sumar 1 Gol"):
                            try:
                                supabase.table("golejadores").upsert({"nom": jugadora_seleccionada, "gols": gols_actuals + 1}, on_conflict="nom").execute()
                                st.success(f"Gol sumat a {jugadora_seleccionada}!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                    with col_bt2:
                        if st.button("➖ Restar 1 Gol") and gols_actuals > 0:
                            try:
                                supabase.table("golejadores").upsert({"nom": jugadora_seleccionada, "gols": gols_actuals - 1}, on_conflict="nom").execute()
                                st.success(f"Gol restat a {jugadora_seleccionada}.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {e}")

            # --- SUBPANELL 4: GOLS PER MINUTS INTERACTIU (+ / -) ---
            with tab_adm_trams:
                st.markdown("#### ⏱️ Actualització Ràpida de Gols per Minuts (+ / -)")
                st.markdown("Llegeix directament de la base de dades i permet sumar o restar gols a cada tram amb un sol clic.")
                
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
                            st.success(f"Gol restat.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

# Executar aplicació
if check_access():
    main()
