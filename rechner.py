import streamlit as st
import trimesh
import tempfile
import os

st.set_page_config(page_title="3D-Print Calc", page_icon="💰")
st.title("🚀 3D-Druck Preis-Kalkulator")

material_daten = {
    "PLA": {"preis_per_g": 0.15, "dichte": 1.25},   
    "PETG": {"preis_per_g": 0.22, "dichte": 1.27}
}

wahl = st.sidebar.selectbox("Material:", list(material_daten.keys()))
infill = st.sidebar.select_slider("Infill %:", options=[15, 40, 70, 100], value=40)

file = st.file_uploader("STL hochladen", type=["stl"])

if file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
        tmp.write(file.getvalue())
        tmp_path = tmp.name
    try:
        mesh = trimesh.load(tmp_path)
        volumen = mesh.volume / 1000  
        gewicht = volumen * material_daten[wahl]["dichte"] * ((infill/100)+0.15)
        preis = max(5.0, gewicht * material_daten[wahl]["preis_per_g"])

        st.success(f"### Preis: {preis:.2f} €")
        st.write(f"Gewicht: {gewicht:.1f}g")
        
        txt = f"Anfrage für {file.name}, Preis: {preis:.2f}€"
        st.markdown(f'[📩 E-Mail](mailto:mixmasteringbyg@gmail.com?body={txt})')
        st.markdown(f'[💬 WhatsApp](https://wa.me/4915563398574?text={txt.replace(" ", "%20")})')
    finally:
        if os.path.exists(tmp_path): os.remove(tmp_path)
