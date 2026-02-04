import streamlit as st
import trimesh
import tempfile
import os
import json
import numpy as np
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# =================================================================
# 1. GLOBALE KONFIGURATION & SETUP
# =================================================================

# Deine Google Drive Ordner-ID (aus deinem Link)
DRIVE_FOLDER_ID = "1Fz-us-qEH6p99bmKqU-nHXfCoh_NrEPq"

# Streamlit Seiten-Konfiguration (Titel & Icon im Browser-Tab)
st.set_page_config(
    page_title="Gian's 3D-Kalkulator",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Individuelles CSS für das "Gian-Design" (Mobile Optimierung)
st.markdown("""
    <style>
    /* Verstecke Streamlit Standard-Menüs */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Buttons stylen: Groß, rund und griffig für Handys */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 4em;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    /* Hover-Effekt für Buttons */
    .stButton>button:hover {
        border: 2px solid #25D366;
        transform: scale(1.02);
    }

    /* Info-Boxen schöner machen */
    .stAlert {
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 2. GOOGLE DRIVE LOGIK (FUNKTIONEN)
# =================================================================

def upload_to_drive(file_path, file_name):
    """
    Diese Funktion verbindet sich mit Google Drive und lädt die Datei hoch.
    Inklusive Fix für Speicherplatz-Probleme bei Service Accounts.
    """
    try:
        # 1. Zugangsdaten aus den Streamlit Secrets laden
        creds_json = st.secrets["gcp_service_account"]
        creds_info = json.loads(creds_json)
        
        # 2. Authentifizierung aufbauen
        creds = service_account.Credentials.from_service_account_info(creds_info)
        service = build('drive', 'v3', credentials=creds)

        # 3. Metadaten für die Datei (Name & Zielordner)
        file_metadata = {
            'name': file_name, 
            'parents': [DRIVE_FOLDER_ID]
        }
        
        # 4. Datei vorbereiten
        media = MediaFileUpload(file_path, resumable=True)
        
        # 5. Der eigentliche Upload-Befehl
        # Wichtig: supportsAllDrives=True erlaubt Nutzung deines Speichers!
        uploaded_file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id',
            supportsAllDrives=True,
            supportsTeamDrives=True
        ).execute()
        
        return uploaded_file.get('id')
        
    except Exception as error:
        st.error(f"❌ Schwerwiegender Drive-Fehler: {str(error)}")
        return None

# =================================================================
# 3. KALKULATIONS-LOGIK & PREISE
# =================================================================

# Material-Konfiguration (Preis pro Gramm & Dichte)
materials = {
    "PLA (Standard)": {"price": 0.15, "density": 1.24},   
    "PETG (Stabil)": {"price": 0.22, "density": 1.27},  
    "PC (High-End)": {"price": 0.45, "density": 1.20} 
}

# =================================================================
# 4. BENUTZEROBERFLÄCHE (UI)
# =================================================================

st.title("💰 3D-Druck Kalkulator")
st.write("Berechne sofort deinen Preis und sende die Datei an Gian.")

# --- SCHRITT 1: EINSTELLUNGEN ---
st.subheader("📋 1. Druck-Einstellungen")
selected_material = st.selectbox("Wähle dein Material aus:", list(materials.keys()))
selected_infill = st.select_slider(
    "Wie stabil soll es sein? (Infill %)", 
    options=[15, 40, 70, 100], 
    value=40,
    help="15% ist leicht, 100% ist massiv."
)

st.divider()

# --- SCHRITT 2: DATEI UPLOAD ---
st.subheader("📂 2. Modell hochladen")
st.info("Bitte lade nur .STL Dateien hoch. Die Analyse startet automatisch.")
uploaded_file = st.file_uploader("Datei hier reinziehen oder klicken", type=["stl"])

# =================================================================
# 5. VERARBEITUNG & AKTIONEN
# =================================================================

if uploaded_file is not None:
    # Erstelle eine temporäre Datei (Sicherheitsstandard)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        path_to_tmp = tmp_file.name

    try:
        # Modell-Analyse mit Trimesh
        with st.spinner('Modell wird analysiert...'):
            mesh_data = trimesh.load(path_to_tmp)
            
            # Volumen in cm³ berechnen
            volume_cm3 = mesh_data.volume / 1000  
            
            # Gewichtsberechnung basierend auf Infill und Materialdichte
            infill_factor = (selected_infill / 100) + 0.12 # 12% Aufschlag für Wände
            estimated_weight = volume_cm3 * materials[selected_material]["density"] * infill_factor
            
            # Endpreis berechnen
            final_price = estimated_weight * materials[selected_material]["price"]
            
            # Mindestbestellwert von 5€
            if final_price < 5.0:
                final_price = 5.0

        # Ergebnis-Box anzeigen
        st.success(f"### Kalkulierter Preis: **{final_price:.2f} €**")
        
        st.markdown(f"""
        **Zusammenfassung:**
        * 📦 Modell: `{uploaded_file.name}`
        * ⚖️ Gewicht: ca. `{estimated_weight:.1f} g`
        * 🧵 Material: `{selected_material}`
        """)

        st.divider()

        # --- SCHRITT 3: BESTÄTIGUNG ODER ABLEHNUNG ---
        st.subheader("🚀 3. Anfrage absenden")
        st.write("Möchtest du dieses Modell jetzt zur Prüfung an Gian senden?")
        
        action_col1, action_col2 = st.columns(2)
        
        with action_col1:
            if st.button("✅ Bestätigen & Hochladen"):
                # Dateiname für Drive generieren (Preis_Material_Name)
                drive_file_name = f"{final_price:.2f}EUR_{selected_material.split(' ')[0]}_{selected_infill}Infill_{uploaded_file.name}"
                
                with st.spinner('Sende an Google Drive...'):
                    success_id = upload_to_drive(path_to_tmp, drive_file_name)
                    
                    if success_id:
                        st.balloons()
                        st.success("Übertragung abgeschlossen!")
                        
                        # WhatsApp Link vorbereiten
                        text_msg = (f"Hi Gian, ich habe gerade mein Modell '{uploaded_file.name}' hochgeladen. "
                                   f"Preis: {final_price:.2f}€ | Material: {selected_material}. "
                                   f"Bitte prüfen!")
                        whatsapp_url = f"https://wa.me/4915563398574?text={text_msg.replace(' ', '%20')}"
                        
                        # WhatsApp Button
                        st.markdown(f'''
                            <a href="{whatsapp_url}" target="_blank" style="text-decoration:none;">
                                <div style="background-color:#25D366; color:white; padding:20px; border-radius:15px; text-align:center; font-weight:bold; font-size:20px; margin-top:10px;">
                                    Jetzt Nachricht auf WhatsApp senden 💬
                                </div>
                            </a>
                        ''', unsafe_allow_html=True)

        with action_col2:
            if st.button("❌ Vorgang abbrechen"):
                st.warning("Abgebrochen. Die Datei wurde vom Server gelöscht.")
                st.info("Du kannst jetzt ein anderes Modell wählen.")

    except Exception as e:
        st.error(f"Fehler bei der Modell-Analyse: {e}")
        st.warning("Stelle sicher, dass es eine gültige STL-Datei ist.")
    
    finally:
        # Lösche die temporäre Datei IMMER (Datenschutz/Speicherplatz)
        if os.path.exists(path_to_tmp):
            os.remove(path_to_tmp)

# =================================================================
# 6. RECHTLICHER BEREICH (VOLLSTÄNDIGES IMPRESSUM)
# =================================================================

st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()

with st.expander("⚖️ Rechtliche Informationen & Datenschutz"):
    st.markdown("""
    ### Impressum
    **Angaben gemäß § 5 DDG:** Andrea Giancarlo Sedda  
    Mix Mastering By G  
    c/o Smartservices GmbH  
    Südstraße 31  
    47475 Kamp-Lintfort  

    **Kontakt:** E-Mail: mixmasteringbyg@gmail.com  
    Telefon: +49 155 63398574  

    **Verantwortlich für den Inhalt:** Andrea Giancarlo Sedda  
    (Anschrift wie oben)

    ---

    ### Urheberrecht & Schutzrechte
    Durch das Hochladen einer Datei bestätigt der Nutzer, dass er entweder der Urheber der Datei ist oder über die ausdrückliche Erlaubnis verfügt, dieses Modell vervielfältigen zu lassen. Mix Mastering By G übernimmt keine Haftung für Marken- oder Urheberrechtsverletzungen durch Kunden-Modelle. Im Falle einer rechtlichen Inanspruchnahme durch Dritte stellt der Kunde den Betreiber von allen Kosten und Ansprüchen frei.

    ---

    ### Datenschutzerklärung
    **1. Datenverarbeitung auf dieser Webseite:** Diese Anwendung läuft auf Streamlit Cloud. Hochgeladene Dateien werden zur Analyse in einem temporären Arbeitsspeicher verarbeitet und nach der Sitzung sofort gelöscht.
    
    **2. Google Drive Speicherung:** Eine dauerhafte Speicherung erfolgt ausschließlich nach deiner expliziten Bestätigung durch Klick auf den "Hochladen"-Button. Die Dateien werden in einem passwortgeschützten Google Drive Ordner gespeichert, auf den nur der Betreiber Zugriff hat.
    
    **3. WhatsApp Kontakt:** Wenn du den WhatsApp-Button nutzt, gelten die Datenschutzrichtlinien von WhatsApp (Meta Platforms).
    """)

# Ende des Codes
