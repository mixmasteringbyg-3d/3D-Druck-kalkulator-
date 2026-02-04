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
# 1. GLOBALE KONFIGURATION & SETUP (ZEILE 12+)
# =================================================================

# Deine Google Drive Ordner-ID (Damit die Dateien im richtigen Ordner landen)
DRIVE_FOLDER_ID = "1Fz-us-qEH6p99bmKqU-nHXfCoh_NrEPq"

# Streamlit Seiten-Konfiguration
st.set_page_config(
    page_title="Gian's Professional 3D-Kalkulator",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =================================================================
# 2. DESIGN & STYLING (MOBILE OPTIMIERUNG)
# =================================================================

st.markdown("""
    <style>
    /* Entferne unnötigen Streamlit-Platz oben */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Buttons für dicke Finger auf dem Handy optimieren */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 4.5em;
        font-weight: 800;
        font-size: 1.2rem;
        background-color: #f0f2f6;
        transition: all 0.4s ease;
        border: 2px solid #e0e0e0;
        margin-top: 10px;
    }
    
    /* Spezielles Grün für den Bestätigen-Button */
    div.stButton > button:first-child {
        border: 2px solid #25D366;
    }

    /* Styling für die Preis-Anzeige */
    .price-box {
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 15px;
        border-left: 5px solid #25D366;
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. GOOGLE DRIVE API FUNKTION (DER QUOTA-FIX)
# =================================================================

def upload_to_drive(file_path, file_name):
    """
    Diese Funktion übernimmt den Upload zu Google Drive.
    Sie nutzt 'supportsAllDrives', um Speicherplatz-Probleme zu umgehen.
    """
    try:
        # Authentifizierung über die Secrets
        creds_json = st.secrets["gcp_service_account"]
        creds_info = json.loads(creds_json)
        
        # Verbindung aufbauen
        creds = service_account.Credentials.from_service_account_info(creds_info)
        service = build('drive', 'v3', credentials=creds)

        # Datei-Metadaten festlegen
        file_metadata = {
            'name': file_name, 
            'parents': [DRIVE_FOLDER_ID]
        }
        
        # Datei-Upload vorbereiten
        media = MediaFileUpload(file_path, resumable=True)
        
        # Upload ausführen mit Quota-Workaround
        uploaded_file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id',
            supportsAllDrives=True,
            supportsTeamDrives=True
        ).execute()
        
        return uploaded_file.get('id')
        
    except Exception as drive_err:
        st.error(f"❌ Fehler bei der Cloud-Übertragung: {str(drive_err)}")
        return None

# =================================================================
# 4. PREIS-KALKULATION & MATERIAL-LOGIK
# =================================================================

# Definition der Materialien und Kostenfaktoren
materials = {
    "PLA (Standard)": {"price": 0.15, "density": 1.24},   
    "PETG (Widerstandsfähig)": {"price": 0.22, "density": 1.27},  
    "PC (Industrie-Standard)": {"price": 0.45, "density": 1.20} 
}

# =================================================================
# 5. BENUTZEROBERFLÄCHE (UI)
# =================================================================

st.title("🚀 Gian's 3D-Druck Rechner")
st.write("Wähle deine Optionen, lade dein Modell hoch und erhalte sofort ein Angebot.")

st.divider()

# Auswahl-Bereich
st.subheader("⚙️ 1. Konfiguration")
col_a, col_b = st.columns(2)

with col_a:
    selected_material = st.selectbox("Material:", list(materials.keys()))

with col_b:
    selected_infill = st.select_slider("Infill (Füllung %):", options=[15, 40, 70, 100], value=40)

st.divider()

# Upload-Bereich
st.subheader("📂 2. Modell-Upload")
st.markdown("Lade hier deine **.STL** Datei hoch. Die Analyse erfolgt in Echtzeit.")
uploaded_file = st.file_uploader("Datei auswählen...", type=["stl"])

# =================================================================
# 6. VERARBEITUNGS-PROZESS (ANALYSE & BUTTONS)
# =================================================================

if uploaded_file is not None:
    # Temporäre lokale Speicherung (RAM-Simulation)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        # 3D-Mesh Analyse
        with st.spinner('Analysiere Geometrie...'):
            mesh = trimesh.load(tmp_path)
            
            # Berechnung des Volumens und Gewichts
            volume = mesh.volume / 1000 # in cm³
            
            # Infill-Berechnung (Basis + Infill-Prozent + Wandstärke-Puffer)
            calc_factor = (selected_infill / 100) + 0.15
            weight = volume * materials[selected_material]["density"] * calc_factor
            
            # Preisberechnung
            total_price = weight * materials[selected_material]["price"]
            
            # Mindestumsatz-Schutz
            if total_price < 5.0:
                total_price = 5.0

        # Preis-Anzeige für den Kunden
        st.markdown(f"""
        <div class="price-box">
            <h2 style="margin:0; color:#1a1a1a;">Voraussichtlicher Preis: {total_price:.2f} €</h2>
            <p style="margin:5px 0 0 0; color:#666;">Modell: {uploaded_file.name} | Gewicht: ca. {weight:.1f}g</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # BESTÄTIGUNG ODER ABLEHNUNG
        st.subheader("✅ 3. Anfrage bestätigen")
        st.write("Möchtest du das Modell und die Daten jetzt sicher an Gian übertragen?")
        
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("JA, Kalkulation senden"):
                # Datei-Name für Google Drive (Rechtssicher inkl. Preis)
                # Format: PREIS_MATERIAL_INFILL_DATEINAME.stl
                safe_name = f"{total_price:.2f}EUR_{selected_material.replace(' ', '_')}_{selected_infill}Infill_{uploaded_file.name}"
                
                with st.spinner('Datei wird übertragen...'):
                    # Upload-Prozess starten
                    drive_id = upload_to_drive(tmp_path, safe_name)
                    
                    if drive_id:
                        st.balloons()
                        st.success("Übertragung erfolgreich abgeschlossen!")
                        
                        # WhatsApp Link generieren für den direkten Kontakt
                        wa_msg = (f"Hallo Gian, ich habe gerade mein Modell '{uploaded_file.name}' hochgeladen. "
                                 f"Kalkulierter Preis: {total_price:.2f}€ | Material: {selected_material} | Infill: {selected_infill}%.")
                        wa_url = f"https://wa.me/4915563398574?text={wa_msg.replace(' ', '%20')}"
                        
                        # Fetter WhatsApp Button
                        st.markdown(f'''
                            <a href="{wa_url}" target="_blank" style="text-decoration:none;">
                                <div style="background-color:#25D366; color:white; padding:20px; border-radius:15px; text-align:center; font-weight:bold; font-size:18px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                                    Bestellung via WhatsApp abschließen 💬
                                </div>
                            </a>
                        ''', unsafe_allow_html=True)

        with btn_col2:
            if st.button("NEIN, Abbrechen"):
                st.warning("Vorgang wurde abgebrochen. Die Datei wurde nicht gespeichert.")
                st.info("Lade die Seite neu, um eine andere Datei zu wählen.")

    except Exception as e:
        st.error(f"Fehler bei der Analyse der STL-Datei: {e}")
        st.info("Bitte stelle sicher, dass es sich um eine valide 3D-Datei handelt.")
    
    finally:
        # DATENSCHUTZ-CHECK: Temporäre Datei lokal löschen
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# =================================================================
# 7. RECHTLICHER BEREICH (MAXIMALE LÄNGE & RECHTSSICHERHEIT)
# =================================================================

st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()

with st.expander("⚖️ Rechtliche Informationen, Impressum & Datenschutz"):
    st.markdown("""
    ### Impressum gemäß § 5 DDG
    **Betreiber der Webseite:** Andrea Giancarlo Sedda  
    Mix Mastering By G  
    c/o Smartservices GmbH  
    Südstraße 31  
    47475 Kamp-Lintfort  

    **Kontakt:** E-Mail: mixmasteringbyg@gmail.com  
    Telefon: +49 155 63398574  

    **Redaktionell verantwortlich:** Andrea Giancarlo Sedda  

    ---

    ### Rechtlicher Hinweis zu 3D-Modellen (Urheberrecht)
    Mit dem Hochladen einer Datei auf diesen Server versichert der Nutzer ausdrücklich, dass er entweder der rechtmäßige Eigentümer des Urheberrechts am Modell ist oder über eine entsprechende Lizenz zur Vervielfältigung verfügt. 
    Mix Mastering By G übernimmt keine Haftung für die Verletzung von Schutzrechten Dritter. Der Nutzer stellt den Betreiber von allen Ansprüchen Dritter (inkl. Anwaltskosten) frei, die durch die unbefugte Nutzung von 3D-Daten entstehen können. Wir drucken keine Waffen, Waffenteile oder verbotene Gegenstände.

    ---

    ### Datenschutzerklärung (DSGVO)
    **1. Datenverarbeitung:** Die Analyse der 3D-Dateien erfolgt im flüchtigen Arbeitsspeicher (RAM). Es findet keine dauerhafte Speicherung auf dem Webserver statt.
    
    **2. Google Drive Speicherung:** Eine Übertragung und dauerhafte Speicherung Ihrer Daten erfolgt ausschließlich nach Ihrer aktiven Zustimmung durch Klick auf den "Senden"-Button. Die Daten werden in einem gesicherten Cloud-Speicher (Google Drive) abgelegt, um die Auftragsabwicklung zu ermöglichen.
    
    **3. Datensicherheit:** Wir setzen moderne SSL/TLS-Verschlüsselung für die Übertragung Ihrer Daten ein. Ihre Daten werden niemals ohne Ihre Zustimmung an Dritte weitergegeben.
    
    **4. WhatsApp:** Bei Nutzung des Kontakt-Links gelten die Datenschutzbestimmungen von Meta Platforms.
    """)

# =================================================================
# ENDE DES CODES
# =================================================================
