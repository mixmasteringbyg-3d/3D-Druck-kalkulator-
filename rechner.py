import streamlit as st
import trimesh
import tempfile
import os

# 1. Seite & Design Konfiguration
st.set_page_config(page_title="3D-Print Calc & Order", page_icon="💰", layout="centered")

# CSS für Mobile-Optimierung und versteckte Menüs
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {width: 100%;}
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 3D-Druck Preis-Kalkulator")
st.markdown("Lade dein Modell hoch und erhalte sofort eine Preisschätzung.")

# 2. Material-Daten & Preise
material_daten = {
    "PLA": {"preis_per_g": 0.15, "dichte": 1.25},   
    "PETG": {"preis_per_g": 0.22, "dichte": 1.27},  
    "PC (Polycarbonat)": {"preis_per_g": 0.45, "dichte": 1.20} 
}

# 3. Hauptbereich Einstellungen (Sichtbar für alle, auch am Handy)
st.subheader("1. Druck-Einstellungen")
wahl = st.selectbox("Material wählen:", list(material_daten.keys()))
infill = st.select_slider("Füllung (Infill %):", options=[15, 40, 70, 100], value=40)

st.divider()

# 4. Datei Upload mit Urheberrechts-Warnung
st.subheader("2. Modell hochladen")
st.warning("⚠️ Mit dem Upload bestätigen Sie, dass Sie die notwendigen Rechte/Lizenzen an der Datei besitzen und keine Schutzrechte Dritter verletzen.")

file = st.file_uploader("STL-Datei hier auswählen", type=["stl"])

if file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
        tmp.write(file.getvalue())
        tmp_path = tmp.name

    try:
        # Modell-Analyse
        mesh = trimesh.load(tmp_path)
        volumen_netto = mesh.volume / 1000  # cm3
        
        # Infill-Berechnung (Basis-Struktur + Infill-Anteil)
        effektive_fullung = (infill / 100) + 0.15 
        gewicht = volumen_netto * material_daten[wahl]["dichte"] * effektive_fullung
        
        # Preisberechnung
        total = gewicht * material_daten[wahl]["preis_per_g"]
        
        # Mindestpreis
        if total < 5.0: total = 5.0

        # Ergebnis-Anzeige
        st.success(f"### Voraussichtlicher Preis: {total:.2f} €")
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.info(f"**Material:** {wahl}")
        with col_res2:
            st.info(f"**Gewicht:** ca. {gewicht:.1f}g")
            
        st.write(f"**Abmessungen:** {mesh.bounding_box.extents[0]:.1f} x {mesh.bounding_box.extents[1]:.1f} x {mesh.bounding_box.extents[2]:.1f} mm")

        # 5. Kontakt-Sektion (Handy-optimiert)
        st.divider()
        st.subheader("3. Anfrage senden")
        
        # Nachrichtentext inkl. Urheberrechts-Bestätigung
        nachricht = (f"Hallo Gian, ich möchte '{file.name}' drucken lassen. "
                     f"Material: {wahl}, Infill: {infill}%. Preis: {total:.2f}€. "
                     f"Ich bestätige hiermit, dass ich die Urheberrechte an der Datei besitze.")
        
        mailto = f"mailto:mixmasteringbyg@gmail.com?subject=Anfrage: {file.name}&body={nachricht}"
        whatsapp = f"https://wa.me/4915563398574?text={nachricht.replace(' ', '%20')}"

        # Große Buttons für Touchscreens
        st.markdown(f"""
            <a href="{whatsapp}" target="_blank" style="text-decoration:none;">
                <div style="background-color:#25D366;color:white;padding:18px;border-radius:12px;text-align:center;font-weight:bold;margin-bottom:15px;font-size:18px;">
                    💬 Via WhatsApp anfragen
                </div>
            </a>
            <a href="{mailto}" style="text-decoration:none;">
                <div style="background-color:#ff4b4b;color:white;padding:18px;border-radius:12px;text-align:center;font-weight:bold;font-size:18px;">
                    📩 Via E-Mail anfragen
                </div>
            </a>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error("Fehler bei der Analyse der STL-Datei. Bitte prüfen Sie das Dateiformat.")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# 6. VOLLSTÄNDIGES RECHTLICHES (DEIN TEXT)
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

    **EU-Streitschlichtung:** Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: [https://ec.europa.eu/consumers/odr/](https://ec.europa.eu/consumers/odr/).  
    Unsere E-Mail-Adresse finden Sie oben im Impressum.  

    **Verbraucherstreitbeilegung/Universalschlichtungsstelle:** Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.

    ---
    ### Haftungsausschluss (Urheberrecht)
    **Wichtiger Hinweis zu 3D-Modellen:** Der Nutzer versichert mit dem Hochladen einer Datei und der Auftragserteilung, dass er der Inhaber der Urheber- und Markenrechte für das übermittelte Modell ist oder über die ausdrückliche Erlaubnis zur Vervielfältigung verfügt.  
    **Mix Mastering By G** übernimmt keine Prüfung der übermittelten Daten auf Verletzung von Schutzrechten Dritter. Sollten Dritte Ansprüche wegen der Verletzung von Urheber- oder Markenrechten geltend machen, stellt der Nutzer Mix Mastering By G von sämtlichen Ansprüchen und Kosten der Rechtsverteidigung frei. Wir drucken keine Waffen oder gesetzeswidrigen Gegenstände.

    ---
    ### Datenschutzerklärung
    **1. Datenerfassung:** Bei Nutzung der Kontakt-Links (E-Mail oder WhatsApp) werden die von Ihnen kalkulierten Daten (Dateiname, Material, Preis) automatisch in Ihr eigene Nachrichtensystem übernommen. Auf diesem Server werden keine Dateien dauerhaft gespeichert.  
    **2. Zweck:** Die Datenübermittlung dient ausschließlich der Bearbeitung Ihrer individuellen Anfrage.  
    **3. Datensicherheit:** Wir nutzen SSL-Verschlüsselung für den Betrieb dieser Webseite. Bitte beachten Sie die Datenschutzrichtlinien von WhatsApp oder Ihrem E-Mail-Anbieter bei der Kontaktaufnahme.
    """)
