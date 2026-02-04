import streamlit as st
import trimesh
import tempfile
import os

# 1. Seite & Design
st.set_page_config(page_title="3D-Print Calc & Order", page_icon="💰", layout="centered")

# CSS für bessere Mobile-Optik (Buttons breiter, Menüs sauberer)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {width: 100%;}
    /* Verhindert das Abschneiden von Text auf kleinen Displays */
    .stSelectbox, .stSlider {margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 3D-Druck Preis-Kalkulator")
st.markdown("Lade dein Modell hoch und erhalte sofort eine Preisschätzung.")

# --- HAUPTBEREICH (Ersetzt die Sidebar für Handys) ---
st.subheader("1. Einstellungen")

material_daten = {
    "PLA": {"preis_per_g": 0.15, "dichte": 1.25},   
    "PETG": {"preis_per_g": 0.22, "dichte": 1.27},  
    "PC (Polycarbonat)": {"preis_per_g": 0.45, "dichte": 1.20} 
}

# Material und Infill direkt untereinander
wahl = st.selectbox("Material wählen:", list(material_daten.keys()))
infill = st.select_slider("Füllung (Infill %):", options=[15, 40, 70, 100], value=40)

st.divider()

# 2. Datei Upload
st.subheader("2. Modell hochladen")
file = st.file_uploader("STL-Datei auswählen", type=["stl"])

if file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
        tmp.write(file.getvalue())
        tmp_path = tmp.name

    try:
        mesh = trimesh.load(tmp_path)
        volumen_netto = mesh.volume / 1000  
        
        effektive_fullung = (infill / 100) + 0.15 
        gewicht = volumen_netto * material_daten[wahl]["dichte"] * effektive_fullung
        total = gewicht * material_daten[wahl]["preis_per_g"]
        
        if total < 5.0: total = 5.0

        # Ergebnis-Anzeige
        st.success(f"### Preis-Schätzung: {total:.2f} €")
        
        # Details übersichtlich auflisten
        st.info(f"**Gewählt:** {wahl} | **Gewicht:** ca. {gewicht:.1f}g")
        st.write(f"Abmessungen: {mesh.bounding_box.extents[0]:.1f} x {mesh.bounding_box.extents[1]:.1f} x {mesh.bounding_box.extents[2]:.1f} mm")

        # --- KONTAKT ---
        st.divider()
        st.subheader("3. Anfrage senden")
        nachricht = f"Hallo Gian, ich möchte '{file.name}' drucken lassen. Material: {wahl}, Infill: {infill}%. Preis: {total:.2f}€."
        mailto = f"mailto:mixmasteringbyg@gmail.com?subject=Anfrage: {file.name}&body={nachricht}"
        whatsapp = f"https://wa.me/4915563398574?text={nachricht.replace(' ', '%20')}"

        # Große Buttons für Touchscreens
        st.markdown(f'<a href="{whatsapp}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:18px;border-radius:12px;text-align:center;font-weight:bold;margin-bottom:15px;font-size:18px;">💬 Via WhatsApp anfragen</div></a>', unsafe_allow_html=True)
        st.markdown(f'<a href="{mailto}" style="text-decoration:none;"><div style="background-color:#ff4b4b;color:white;padding:18px;border-radius:12px;text-align:center;font-weight:bold;font-size:18px;">📩 Via E-Mail anfragen</div></a>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Fehler bei der Analyse: Das Modell konnte nicht gelesen werden.")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# --- 5. DEIN ORIGINALES IMPRESSUM & DATENSCHUTZ (VOLLSTÄNDIG) ---
st.divider()
with st.expander("Rechtliche Informationen (Impressum & Datenschutz)"):
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

    **EU-Streitschlichtung:** Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: [https://ec.europa.eu/consumers/odr/](https://ec.europa.eu/consumers/odr/).  
    Unsere E-Mail-Adresse finden Sie oben im Impressum.  

    **Verbraucherstreitbeilegung/Universalschlichtungsstelle:** Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.

    ---
    ### Datenschutzerklärung
    **1. Datenerfassung:** Bei Nutzung der Kontakt-Links (E-Mail oder WhatsApp) werden die von Ihnen kalkulierten Daten (Dateiname, Material, Preis) automatisch in Ihr eigene Nachrichtensystem übernommen. Auf diesem Server werden keine Dateien dauerhaft gespeichert.  
    **2. Zweck:** Die Datenübermittlung dient ausschließlich der Bearbeitung Ihrer individuellen Anfrage.  
    **3. Datensicherheit:** Wir nutzen SSL-Verschlüsselung für den Betrieb dieser Webseite. Bitte beachten Sie die Datenschutzrichtlinien von WhatsApp oder Ihrem E-Mail-Anbieter bei der Kontaktaufnahme.
    """)
