import streamlit as st
import trimesh
import tempfile
import os

# 1. Seite & Design
st.set_page_config(page_title="3D-Print Calc", page_icon="💰")

st.title("🚀 3D-Druck Preis-Kalkulator")

# 2. Material-Preise
material_daten = {
    "PLA": {"preis_per_g": 0.15, "dichte": 1.25},   
    "PETG": {"preis_per_g": 0.22, "dichte": 1.27},
    "PC (Polycarbonat)": {"preis_per_g": 0.45, "dichte": 1.20} 
}

# 3. Seitenleiste
st.sidebar.header("Material & Infill")
wahl = st.sidebar.selectbox("Material:", list(material_daten.keys()))
infill = st.sidebar.select_slider("Infill %:", options=[15, 40, 70, 100], value=40)

# 4. Datei Upload
file = st.file_uploader("STL hochladen", type=["stl"])

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

        st.success(f"### Preis: {total:.2f} €")
        st.write(f"**Gewicht:** {gewicht:.1f}g")
        
        st.divider()
        
        # Nachricht für die Buttons
        nachricht = f"Hallo Gian, ich möchte '{file.name}' drucken. Material: {wahl}, Infill: {infill}%. Preis: {total:.2f}€."
        mailto = f"mailto:mixmasteringbyg@gmail.com?subject=3D-Druck Anfrage&body={nachricht}"
        whatsapp = f"https://wa.me/4915563398574?text={nachricht.replace(' ', '%20')}"

        # Buttons im Original-Design
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<a href="{mailto}" style="text-decoration:none;"><div style="background-color:#ff4b4b;color:white;padding:12px;border-radius:10px;text-align:center;font-weight:bold;">📩 E-Mail senden</div></a>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<a href="{whatsapp}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:12px;border-radius:10px;text-align:center;font-weight:bold;">💬 WhatsApp senden</div></a>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Fehler: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# 5. DEIN IMPRESSUM 1ZU1
st.divider()
with st.expander("⚖️ Impressum & Datenschutz"):
    st.markdown("""
    ### Impressum
    **Angaben gemäß § 5 DDG:** Andrea Giancarlo Sedda  
    Mix Mastering By G  
    c/o Smartservices GmbH  
    Südstraße 31  
    47475 Kamp-Lintfort  

    **Kontakt:** Telefon: +49 155 63398574  
    E-Mail: mixmasteringbyg@gmail.com  

    **Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV:** Andrea Giancarlo Sedda  
    (Anschrift wie oben)  

    **EU-Streitschlichtung:** Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit:  
    [https://ec.europa.eu/consumers/odr/](https://ec.europa.eu/consumers/odr/)  
    Unsere E-Mail-Adresse finden Sie oben im Impressum.  

    **Verbraucherstreitbeilegung / Universalschlichtungsstelle:** Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.  

    ---

    ### Datenschutz
    Die Betreiber dieser Seiten nehmen den Schutz Ihrer persönlichen Daten sehr ernst. Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Datenschutzvorschriften sowie dieser Datenschutzerklärung.  

    **Datenerfassung auf dieser Webseite:** Die Nutzung dieser Webseite ist ohne Angabe personenbezogener Daten möglich. Wenn Sie eine STL-Datei hochladen, wird diese nur temporär zur Berechnung verarbeitet und nicht dauerhaft gespeichert.  

    **Kontakt:** Wenn Sie uns per E-Mail oder WhatsApp kontaktieren, werden Ihre Angaben zwecks Bearbeitung der Anfrage gespeichert. Diese Daten geben wir nicht ohne Ihre Einwilligung weiter.
    """)
