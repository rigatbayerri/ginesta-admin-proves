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
@st.cache_data(ttl=3600)
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

# --- ESTIL I COLORS CORPORATIUS: REDISSENY VISUAL V2 ---
st.markdown("""
<style>
:root {
  --ginesta: #5c2d73;
  --ginesta-dark: #3d1b50;
  --ginesta-light: #efe7f5;
  --ginesta-pale: #f8f5fb;
  --ink: #211827;
  --muted: #746b7b;
  --line: #e8e0ed;
  --surface: #ffffff;
}
.stApp { background: #f7f5fa; color: var(--ink); }
[data-testid="stAppViewContainer"] > .main .block-container {
  max-width: 1440px; padding-top: 1.5rem; padding-bottom: 3rem;
}
/* Typography: preserve readable contrast without overriding every span. */
h1, h2, h3, h4, h5, h6 { color: var(--ginesta-dark); letter-spacing: -0.025em; }
p, label, [data-testid="stMarkdownContainer"] { color: var(--ink); }
[data-testid="stCaptionContainer"] { color: var(--muted); }
/* Premium buttons */
.stButton > button, div.stFormSubmitButton > button {
  border: 1px solid var(--ginesta) !important; border-radius: 11px !important;
  background: var(--ginesta) !important; color: #fff !important;
  font-weight: 700 !important; min-height: 2.65rem; padding: .55rem 1rem !important;
  transition: transform .15s ease, box-shadow .15s ease, background .15s ease;
  box-shadow: 0 3px 9px rgba(92,45,115,.12);
}
.stButton > button *, div.stFormSubmitButton > button * { color: #fff !important; }
.stButton > button:hover, div.stFormSubmitButton > button:hover {
  background: var(--ginesta-dark) !important; border-color: var(--ginesta-dark) !important;
  box-shadow: 0 5px 14px rgba(61,27,80,.2); transform: translateY(-1px);
}
.stButton > button:focus, div.stFormSubmitButton > button:focus { outline: 3px solid #d8c2e5 !important; }
/* Inputs */
.stTextInput input, .stNumberInput input, .stDateInput input, .stTimeInput input,
.stTextArea textarea {
    
