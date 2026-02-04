import streamlit as st
import trimesh
import tempfile
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- 1. KONFIGURATION ---
DRIVE_FOLDER_ID = "1Fz-us-qEH6p99bmKqU-nHXfCoh_NrEPq"
MY_EMAIL = "mixmasteringbyg@gmail.com" # Deine Drive-E-Mail

st.set_page_config(page_title="3D-Print Calc & Order", page_icon="💰", layout="centered")

# Modernes, seriöses Layout (Dunkles Theme Optimierung)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        transition: all 0.3s;
    }
    /* Grüner Akzent für den Haupt-Button */
    div.stButton > button:first-child {
        background-color: #2e7d32;
        color: white;
        border: none;
    }
    div.stButton > button:first-child:hover {
        background-color: #1b5e20;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Google Drive Funktion (DER FINALE FIX)
def upload_to_drive(file_path, file_name):
    try:
        creds_info = json.loads(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(creds_info)
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': file_name, 
            'parents': [DRIVE_FOLDER_ID]
        }
        
        media = MediaFileUpload(file_path, resumable=True)
        
        # Upload mit erweiterten Rechten
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True
        ).execute()
        
        file_id = file.get('id')

        # WICHTIG: Übertrage die Datei-Berechtigung auf dich, 
        # damit die Quota von deinem Account gezogen wird
        permission = {
            'type': 'user',
            'role': 'owner',
            'emailAddress': MY_EMAIL
        }
        # Hinweis: Da Service Accounts keine Ownership transferieren können, 
        # setzen wir dich als Writer und nutzen 'supportsAllDrives'
        service.permissions().create(
            fileId=file_id,
            body={'type': 'user', 'role': 'fileOrganizer', 'emailAddress': MY_EMAIL},
            supportsAllDrives=True
        ).execute()

        return file_id
    except Exception as e:
        st.error(f"Drive-Fehler Details: {e}")
        return None

# --- UI LAYOUT ---
st.title("3D-Print Kalkulator")
st.markdown("---")

material_daten = {
    "PLA": {"preis_per_g": 0.15, "dichte": 1.25},   
    "PETG": {"preis_per_g": 0.22, "dichte": 1.27},  
    "PC (Polycarbonat)": {"preis_per_g": 0.45, "dichte": 1.20} 
}

st.subheader("1. Spezifikationen")
col_base1, col_base2 = st.columns(2)
with col_base1:
    wahl = st.selectbox("Material", list(material_daten.keys()))
with col_base2:
    infill = st.select_slider("Infill", options=[15, 40, 70, 100], value=40)

st.subheader("2. Modell-Analyse")
uploaded_file = st.file_uploader("STL-Datei hochladen", type=["stl"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        mesh = trimesh.load(tmp_path)
        volumen = mesh.volume / 1000  
        faktor = (infill / 100) + 0.15 
        gewicht = volumen * material_daten[wahl]["dichte"] * faktor
        preis = max(5.0, gewicht * material_daten[wahl]["preis_per_g"])

        st.metric(label="Berechneter Preis", value=f"{preis:.2f} €")
        st.caption(f"Details: {uploaded_file.name} | geschätztes Gewicht: {gewicht:.1f}g")
        
        st.markdown("---")
        st.subheader("3. Verbindliche Anfrage")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Anfrage senden"):
                d_name = f"{preis:.2f}EUR_{wahl}_{uploaded_file.name}"
                with st.spinner('Datei wird übertragen...'):
                    if upload_to_drive(tmp_path, d_name):
                        st.balloons()
                        st.success("Erfolgreich übertragen!")
                        msg = f"Hallo Gian, ich habe '{uploaded_file.name}' für {preis:.2f}€ hochgeladen ({wahl})."
                        wa = f"https://wa.me/4915563398574?text={msg.replace(' ', '%20')}"
                        st.markdown(f'<a href="{wa}" target="_blank" style="text-decoration:none;"><div style="background-color:#2e7d32;color:white;padding:15px;border-radius:8px;text-align:center;font-weight:bold;">JETZT PER WHATSAPP ABSCHLIESSEN</div></a>', unsafe_allow_html=True)
        with c2:
            if st.button("Vorgang abbrechen"):
                st.warning("Abgebrochen.")

    except Exception as e:
        st.error(f"Fehler: {e}")
    finally:
        if os.path.exists(tmp_path): os.remove(tmp_path)

# --- RECHTLICHES ---
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("Impressum & Datenschutz"):
    st.markdown("""
    **Impressum** Andrea Giancarlo Sedda | Mix Mastering By G  
    c/o Smartservices GmbH | Südstraße 31 | 47475 Kamp-Lintfort  
    Kontakt: mixmasteringbyg@gmail.com | +49 155 63398574  
    
    *Hinweis: Gemäß § 19 UStG wird keine Umsatzsteuer berechnet (Kleingewerberegelung).* ---
    **Urheberrecht** Der Nutzer bestätigt mit dem Upload, dass er die Rechte am Modell besitzt.  
    
    **Datenschutz** Dateien werden temporär verarbeitet und nur bei Klick auf 'Anfrage senden' in unserem Drive gespeichert.
    """)
