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

st.set_page_config(page_title="3D-Print Calc & Order", page_icon="💰", layout="centered")

# Modernes & cooles Design
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        height: 3.5em;
        font-weight: bold;
        font-size: 1.1rem;
        transition: 0.3s;
    }
    div.stButton > button:first-child {
        background-color: #25D366;
        color: white;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Google Drive Funktion (DER FINALE QUOTA-FIX)
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
        
        # FIX: supportsAllDrives & ignoreDefaultVisibility zwingen Google,
        # deinen Speicherplatz zu nutzen, statt den des Bots.
        file_drive = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id',
            supportsAllDrives=True,
            ignoreDefaultVisibility=True
        ).execute()
        return file_drive.get('id')
    except Exception as e:
        st.error(f"⚠️ Drive-Fehler: {e}")
        return None

# --- HAUPTBEREICH ---
st.title("🚀 3D-Druck Preis-Kalkulator")

material_daten = {
    "PLA": {"preis_per_g": 0.15, "dichte": 1.25},   
    "PETG": {"preis_per_g": 0.22, "dichte": 1.27},  
    "PC (Polycarbonat)": {"preis_per_g": 0.45, "dichte": 1.20} 
}

st.subheader("⚙️ 1. Konfiguration")
wahl = st.selectbox("Material wählen:", list(material_daten.keys()))
infill = st.select_slider("Füllung (Infill %):", options=[15, 40, 70, 100], value=40)

st.divider()

st.subheader("📂 2. Modell hochladen")
st.caption("⚠️ Wichtig: Nur .stl Dateien. Mit dem Upload bestätigen Sie die Urheberrechte.")
uploaded_file = st.file_uploader("Wähle deine Datei", type=["stl"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        mesh = trimesh.load(tmp_path)
        volumen_netto = mesh.volume / 1000  
        effektive_fullung = (infill / 100) + 0.15 
        gewicht = volumen_netto * material_daten[wahl]["dichte"] * effektive_fullung
        total = gewicht * material_daten[wahl]["preis_per_g"]
        if total < 5.0: total = 5.0

        st.info(f"📦 Modell: {uploaded_file.name} | ⚖️ Gewicht: ca. {gewicht:.1f}g")
        st.success(f"### Kalkulierter Preis: {total:.2f} €")
        
        st.divider()
        st.subheader("📩 3. Bestätigung")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Ja, kalkulieren & senden"):
                drive_name = f"{total:.2f}EUR_{wahl}_{uploaded_file.name}"
                with st.spinner('Übertragung...'):
                    if upload_to_drive(tmp_path, drive_name):
                        st.success(f"Erfolgreich hochgeladen!")
                        st.balloons()
                        nachricht = (f"Hallo Gian, ich habe '{uploaded_file.name}' hochgeladen. "
                                     f"Preis: {total:.2f}€, Material: {wahl}. Ich bestätige die Urheberrechte.")
                        wa_link = f"https://wa.me/4915563398574?text={nachricht.replace(' ', '%20')}"
                        st.markdown(f'<a href="{wa_link}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:20px;border-radius:15px;text-align:center;font-weight:bold;font-size:18px;">💬 Jetzt per WhatsApp bestellen</div></a>', unsafe_allow_html=True)

        with col2:
            if st.button("❌ Abbrechen & Löschen"):
                st.warning("Vorgang abgebrochen.")

    except Exception as e:
        st.error(f"Fehler: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# --- DEIN VOLLSTÄNDIGES IMPRESSUM & DATENSCHUTZ ---
st.divider()
with st.expander("⚖️ Impressum & Datenschutz"):
    st.markdown("""
    ### Impressum
    **Angaben gemäß § 5 DDG:** Andrea Giancarlo Sedda  
    Mix Mastering By G  
    c/o Smartservices GmbH  
    Südstraße 31  
    47475 Kamp-Lintfort  

    **Kontakt:** E-Mail: mixmasteringbyg@gmail.com  
    Telefon: +49 155 63398574  

    **Umsatzsteuer:** Gemäß § 19 UStG wird keine Umsatzsteuer berechnet (Kleingewerberegelung).  

    **Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV:** Andrea Giancarlo Sedda  
    (Anschrift wie oben)  

    ---

    ### Urheberrecht & Haftung
    Der Nutzer versichert, dass er alle Rechte an den hochgeladenen Dateien besitzt. Mix Mastering By G führt keine Prüfung auf Markenrechtsverletzungen durch. Mit dem Hochladen stellt der Nutzer den Betreiber von allen Ansprüchen Dritter frei. Der Nutzer haftet für alle Schäden, die durch die Verletzung von Urheberrechten oder sonstigen Schutzrechten entstehen.

    ---

    ### Datenschutzerklärung
    **1. Datenschutz auf einen Blick** Die Analyse Ihrer Dateien erfolgt temporär im RAM. Eine dauerhafte Speicherung Ihrer STL-Daten in unserem Google Drive erfolgt erst nach Ihrer ausdrücklichen Bestätigung durch den Versand-Button.

    **2. Datenerfassung auf dieser Website** Die Datenverarbeitung auf dieser Website erfolgt durch den Websitebetreiber. Die von Ihnen hochgeladenen Dateien werden zum Zwecke der Preiskalkulation und Auftragsabwicklung verarbeitet.

    **3. Datensicherheit** Wir setzen moderne Sicherheitsmaßnahmen ein, um Ihre Daten vor unbefugtem Zugriff zu schützen. Nicht gesendete Dateien werden sofort nach der Sitzung gelöscht.

    **4. Analyse-Tools und Tools von Drittanbietern** Wir nutzen Google Drive zur Speicherung Ihrer Auftragsdateien. Es gelten die Datenschutzbestimmungen von Google. Bei Nutzung des WhatsApp-Buttons gelten die Datenschutzbestimmungen von WhatsApp (Meta).
    """)
