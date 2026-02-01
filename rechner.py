import streamlit as st
import trimesh
import tempfile
import os

# 1. Seite & Design
st.set_page_config(page_title="3D-Print Calc", page_icon="💰")

st.title("🚀 3D-Druck Preis-Kalkulator")

# 2. Material-Preise (Wieder inklusive PC!)
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
        # Berechnung
        mesh = trimesh.load(tmp_path)
        volumen_netto = mesh.volume / 1000  
        effektive_fullung = (infill / 100) + 0.15 
        gewicht = volumen_netto * material_daten[wahl]["dichte"] * effektive_fullung
        total = gewicht * material_daten[wahl]["preis_per_g"]
        
        # Mindestpreis 5€
        if total < 5.0: total = 5.0

        # Ergebnisanzeige (wie im Screenshot)
        st.success(f"### Preis: {total:.2f} €")
        st.write(f"**Gewicht:** {gewicht:.1f}g")
        
        st.divider()
        
        # Kontakt-Links
        nachricht = f"Anfrage für {file.name}, Material: {wahl}, Infill: {infill}%. Preis: {total:.2f}€"
        mailto = f"mailto:mixmasteringbyg@gmail.com?subject=3D-Druck Anfrage&body={nachricht}"
        whatsapp = f"https://wa.me/4915563398574?text={nachricht.replace(' ', '%20')}"

        st.markdown(f'[📩 E-Mail senden]({mailto})')
        st.markdown(f'[💬 WhatsApp senden]({whatsapp})')

    except Exception as e:
        st.error(f"Fehler: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# 5. Impressum (Platzhalter am Ende)
st.divider()
with st.expander("Impressum"):
    st.write("Mix Mastering By G | Andrea Giancarlo Sedda")
