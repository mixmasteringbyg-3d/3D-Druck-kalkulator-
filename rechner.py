import streamlit as st
import trimesh
import tempfile
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- 1. KONFIGURATION & DRIVE-ID ---
# Hier ist deine ID aus dem Screenshot
DRIVE_FOLDER_ID = "1Fz-us-qEH6p99bmKqU-nHXfCoh_NrEPq"

# 2. Seite & Design (Mobile Optimierung)
st.set_page_config(page_title="3D-Print Calc & Order", page_icon="💰", layout="centered")

# CSS für Styling und Ausblenden von Streamlit-Elementen
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {width: 100%; border-radius: 15px; height: 3.5em; font-weight: bold; font-size: 18px;}
    .stSelectbox, .stSlider {margin-bottom: 20px;}
    div.stButton > button:first-child { background-color: #25D366; color: white; border: none; } /* WhatsApp/Senden Button Grün */
    </style>
    """, unsafe_allow_html=True)

# 3. Google Drive Upload Funktion
def upload_to_drive(file_path, file_name):
    try:
        # Lädt die Zugangsdaten aus den Streamlit Secrets (wichtig fürs Hosting)
        creds_info = json.loads(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(creds_info)
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {'name': file_name, 'parents': [DRIVE_FOLDER_ID]}
        media = MediaFileUpload(file_path, resumable=True)
        file_drive = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file_drive.get('id')
    except Exception as e:
        st.error(f"❌ Drive-Fehler: {e}")
        return None

# 4. Haupt-Interface
st.title("🚀 3D-Druck Preis-Kalkulator")
st.markdown("Kalkuliere deinen Preis und sende dein Modell direkt an mich.")

# 5. Material & Preise
material_daten = {
    "PLA": {"preis_per_g": 0.15, "dichte": 1.25},   
    "PETG": {"preis_per_g": 0.22, "dichte": 1.27},  
    "PC (Polycarbonat)": {"preis_per_g": 0.45, "dichte": 1.20} 
}

# 6. Einstellungen (Zentral für Mobile)
st.subheader("1. Druck-Einstellungen")
wahl = st.selectbox("Material wählen:", list(material_daten.keys()))
infill = st.select_slider("Füllung (Infill %):", options=[15, 40, 70, 100], value=40)

st.divider()

# 7. Datei Upload & Analyse
st.subheader("2. Modell hochladen")
st.warning("⚠️ Mit dem Upload bestätigen Sie, dass Sie die notwendigen Rechte/Lizenzen an der Datei besitzen.")
uploaded_file = st.file_uploader("STL-Datei auswählen", type=["stl"])

if uploaded_file:
    # Temporäre Speicherung zur Analyse (Wird im RAM/Temp-Ordner gehalten)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        # 3D-Analyse
        mesh = trimesh.load(tmp_path)
        volumen_netto = mesh.volume / 1000  # cm3
        
        # Berechnung (Basis + Infill-Anteil)
        effektive_fullung = (infill / 100) + 0.15 
        gewicht = volumen_netto * material_daten[wahl]["dichte"] * effektive_fullung
        total = gewicht * material_daten[wahl]["preis_per_g"]
        
        # Mindestpreis check
        if total < 5.0: total = 5.0

        # Ergebnisanzeige
        st.success(f"### Preis-Schätzung: {total:.2f} €")
        st.info(f"**Details:** {uploaded_file.name} | ca. {gewicht:.1f}g | Material: {wahl}")

        st.divider()

        # --- 8. BESTÄTIGUNGS-BEREICH ---
        st.subheader("3. Bestätigung & Versand")
        st.write("Möchten Sie dieses Modell für diesen Preis an Gian übertragen?")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Bestätigen & Senden"):
                # Datei-Name für Drive inkl. aller Infos
                drive_name = f"{total:.2f}EUR_{wahl}_{infill}Infill_{uploaded_file.name}"
                
                with st.spinner('Datei wird sicher an Gian übertragen...'):
                    drive_id = upload_to_drive(tmp_path, drive_name)
                    
                    if drive_id:
                        st.balloons()
                        st.success("Übertragung erfolgreich!")
                        
                        # Kontakt-Link generieren
                        nachricht = (f"Hallo Gian, ich habe '{uploaded_file.name}' gerade hochgeladen. "
                                     f"Preis: {total:.2f}€, Material: {wahl}, Infill: {infill}%. "
                                     f"Ich bestätige hiermit, dass ich die Urheberrechte besitze.")
                        
                        whatsapp_link = f"https://wa.me/4915563398574?text={nachricht.replace(' ', '%20')}"
                        
                        st.markdown(f'<a href="{whatsapp_link}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:18px;border-radius:12px;text-align:center;font-weight:bold;font-size:18px;">💬 Jetzt per WhatsApp kontaktieren</div></a>', unsafe_allow_html=True)

        with col2:
            if st.button("❌ Abbrechen / Löschen"):
                st.warning("Vorgang abgebrochen. Die Datei wurde nicht übertragen.")
                # Der Code geht dann einfach weiter und löscht die Temp-Datei

    except Exception as e:
        st.error("Fehler: Das Modell konnte nicht korrekt gelesen werden.")
    finally:
        # WICHTIG: Datei vom lokalen Server löschen (Datenschutz!)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# --- 9. RECHTLICHES (VOLLSTÄNDIGES IMPRESSUM & DATENSCHUTZ) ---
st.divider()
with st.expander("Rechtliche Informationen (Impressum, Datenschutz & Haftung)"):
    st.markdown("""
    ### Impressum
    **Angaben gemäß § 5 DDG:** Andrea Giancarlo Sedda  
    Mix Mastering By G  
    c/o Smartservices GmbH  
    Südstraße 31  
    47475 Kamp-Lintfort  

    **Kontakt:** E-Mail: mixmasteringbyg@gmail.com  
    Telefon: +49 155 63398574  

    **Umsatzsteuer-ID:** Gemäß § 19 UStG wird keine Umsatzsteuer berechnet und daher keine Umsatzsteuer-Identifikationsnummer ausgewiesen.  

    **Redaktionell verantwortlich:** Andrea Giancarlo Sedda  
    c/o Smartservices GmbH  
    Südstraße 31  
    47475 Kamp-Lintfort  

    **EU-Streitschlichtung:** Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: [https://ec.europa.eu/consumers/odr/](https://ec.europa.eu/consumers/odr/). Unsere E-Mail-Adresse finden Sie oben im Impressum.  

    **Verbraucherstreitbeilegung/Universalschlichtungsstelle:** Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.

    ---
    ### Haftungsausschluss (Urheberrecht)
    **Wichtiger Hinweis zu 3D-Modellen:** Der Nutzer versichert mit dem Hochladen einer Datei und der Auftragserteilung, dass er der Inhaber der Urheber- und Markenrechte für das übermittelte Modell ist oder über die ausdrückliche Erlaubnis zur Vervielfältigung verfügt.  
    **Mix Mastering By G** übernimmt keine Prüfung der übermittelten Daten auf Verletzung von Schutzrechten Dritter. Sollten Dritte Ansprüche wegen der Verletzung von Urheber- oder Markenrechten geltend machen, stellt der Nutzer Mix Mastering By G von sämtlichen Ansprüchen und Kosten der Rechtsverteidigung frei. Wir drucken keine Waffen oder gesetzeswidrigen Gegenstände.

    ---
    ### Datenschutzerklärung
    **1. Datenerfassung:** Bei Nutzung der Kontakt-Links (WhatsApp) werden die von Ihnen kalkulierten Daten automatisch übernommen.  
    **2. Temporäre Speicherung:** Ihre Dateien werden zur Analyse kurzzeitig in einem flüchtigen Zwischenspeicher verarbeitet. Eine dauerhafte Speicherung auf diesem Webserver findet **nicht** statt.  
    **3. Cloud-Übertragung:** Erst wenn Sie explizit auf "Bestätigen & Senden" klicken, wird die Datei verschlüsselt in unser Google Drive übertragen. Dateien von nicht abgeschlossenen Vorgängen werden sofort vom Server gelöscht.  
    **4. Datensicherheit:** Wir nutzen SSL-Verschlüsselung. Bitte beachten Sie die Datenschutzrichtlinien von WhatsApp bei der Kontaktaufnahme.
    """)
