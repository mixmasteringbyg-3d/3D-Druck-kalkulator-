import streamlit as st
import trimesh
import tempfile
import os

# 1. Seite & Design
st.set_page_config(page_title="3D-Print Calc & Order", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Deine gewünschte Überschrift
st.title("🚀 3D-Druck Preis-Kalkulator")
st.markdown("Lade dein Modell hoch und erhalte sofort eine Preisschätzung.")

# 2. Material-Preise (Deutliche Unterschiede für PLA, PETG, PC)
material_daten = {
    "PLA": {"preis_per_g": 0.15, "dichte": 1.25},   
    "PETG": {"preis_per_g": 0.22, "dichte": 1.27},  
    "PC (Polycarbonat)": {"preis_per_g": 0.45, "dichte": 1.20} 
}

# 3. Seitenleiste
st.sidebar.header("🔧 Druck-Optionen")
wahl = st.sidebar.selectbox("Wähle dein Material:", list(material_daten.keys()))
infill = st.sidebar.select_slider("Füllung (Infill):", options=[15, 40, 70, 100], value=40)

# 4. Datei Upload
file = st.file_uploader("STL-Datei hier hochladen", type=["stl"])

if file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
        tmp.write(file.getvalue())
        tmp_path = tmp.name

    try:
        # Modell laden und analysieren
        mesh = trimesh.load(tmp_path)
        volumen_netto = mesh.volume / 1000  # cm3
        
        # Infill-Logik: Basisgewicht + Infill-Anteil
        effektive_fullung = (infill / 100) + 0.15 
        gewicht = volumen_netto * material_daten[wahl]["dichte"] * effektive_fullung
        
        # Preisberechnung
        total = gewicht * material_daten[wahl]["preis_per_g"]
        
        # Mindestpreis (damit kleine Teile nicht zu billig werden)
        if total < 5.0: total = 5.0

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📦 Modelldetails")
            st.write(f"**Datei:** {file.name}")
            st.write(f"**Abmessungen:** {mesh.bounding_box.extents[0]:.1f} x {mesh.bounding_box.extents[1]:.1f} x {mesh.bounding_box.extents[2]:.1f} mm")
            st.info("Modell erfolgreich analysiert.")

        with col2:
            st.subheader("💰 Dein Angebot")
            st.success(f"### Preis: {total:.2f} €")
            st.write(f"**Geschätztes Gewicht:** {gewicht:.1f} g")
            
            st.divider()
            nachricht = f"Hallo Gian, ich möchte '{file.name}' drucken lassen. Material: {wahl}, Infill: {infill}%. Preis: {total:.2f}€."
            mailto = f"mailto:mixmasteringbyg@gmail.com?subject=Anfrage: {file.name}&body={nachricht}"
            whatsapp = f"https://wa.me/4915563398574?text={nachricht.replace(' ', '%20')}"

            c_mail, c_wa = st.columns(2)
            c_mail.markdown(f'<a href="{mailto}" style="text-decoration:none;"><div style="background-color:#ff4b4b;color:white;padding:12px;border-radius:10px;text-align:center;font-weight:bold;">📩 E-Mail</div></a>', unsafe_allow_html=True)
            c_wa.markdown(f'<a href="{whatsapp}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:12px;border-radius:10px;text-align:center;font-weight:bold;">💬 WhatsApp</div></a>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Fehler: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# 5. DEIN ORIGINALES IMPRESSUM & DATENSCHUTZ
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