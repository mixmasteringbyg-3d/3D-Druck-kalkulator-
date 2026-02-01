import streamlit as st
import trimesh
import tempfile
import os

# 1. Seite & Design
st.set_page_config(page_title="3D-Print Calc", page_icon="💰", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 3D-Druck Preis-Kalkulator")

# 2. Material-Preise
material_daten = {
    "PLA": {"preis_per_g": 0.15, "dichte": 1.25},   
    "PETG": {"preis_per_g": 0.22, "dichte": 1.27},
    "PC (Polycarbonat)": {"preis_per_g": 0.45, "dichte": 1.20} 
}

# 3. Seitenleiste
st.sidebar.header("🔧 Optionen")
wahl = st.sidebar.selectbox("Material wählen:", list(material_daten.keys()))
infill = st.sidebar.select_slider("Füllung (Infill) %:", options=[15, 40, 70, 100], value=40)

# 4. Datei Upload
file = st.file_uploader("STL-Datei hochladen", type=["stl"])

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

        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            st.success(f"### Preis-Vorschlag: {total:.2f} €")
            st.info(f"Voraussichtliches Gewicht: {gewicht:.1f}g (Material: {wahl})")

        with col_side:
            st.subheader("Anfrage senden")
            nachricht = f"Hallo Gian, ich möchte '{file.name}' drucken. Material: {wahl}, Infill: {infill}%. Preis: {total:.2f}€."
            mailto = f"mailto:mixmasteringbyg@gmail.com?subject=3D-Druck Anfrage&body={nachricht}"
            whatsapp = f"https://wa.me/4915563398574?text={nachricht.replace(' ', '%20')}"

            st.markdown(f'<a href="{mailto}" style="text-decoration:none;"><div style="background-color:#ff4b4b;color:white;padding:12px;border-radius:10px;text-align:center;font-weight:bold;margin-bottom:10px;">📩 E-Mail</div></a>', unsafe_allow_html=True)
            st.markdown(f'<a href="{whatsapp}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:12px;border-radius:10px;text-align:center;font-weight:bold;">💬 WhatsApp</div></a>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Fehler: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# 5. DEIN VOLLSTÄNDIGES IMPRESSUM & RECHTSHINWEISE
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

    **Umsatzsteuer-ID:** Gemäß § 19 UStG wird keine Umsatzsteuer berechnet und daher keine Umsatzsteuer-Identifikationsnummer ausgewiesen.  

    **Redaktionell verantwortlich:** Andrea Giancarlo Sedda  
    c/o Smartservices GmbH  
    Südstraße 31  
    47475 Kamp-Lintfort  

    **EU-Streitschlichtung:** Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: https://ec.europa.eu/consumers/odr/.  
    Unsere E-Mail-Adresse finden Sie oben im Impressum.  

    **Verbraucherstreitbeilegung/Universalschlichtungsstelle:** Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.  

    ---

    ### ⚠️ Wichtiger Hinweis zu Urheberrechten
    Mit dem Hochladen einer Datei bestätigt der Kunde, dass er über die notwendigen Lizenzen für die Vervielfältigung verfügt. Mix Mastering By G übernimmt keine Haftung für Verletzungen von Urheber-, Patent- oder Markenrechten Dritter. Der Kunde stellt Mix Mastering By G von sämtlichen Ansprüchen Dritter frei.

    ---

    ### Datenschutzerklärung
    **STL-Dateien:** Dateien werden nur kurzzeitig zur Berechnung verarbeitet und danach unmittelbar gelöscht. Es findet keine dauerhafte Speicherung statt.  
    **Kontakt:** Bei Kontakt per E-Mail oder WhatsApp speichern wir Ihre Angaben zwecks Bearbeitung der Anfrage.  
    **Hosting:** Diese Webseite wird über Streamlit Cloud gehostet.
    """)
