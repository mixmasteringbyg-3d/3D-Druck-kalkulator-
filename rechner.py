import streamlit as st
import trimesh
import tempfile
import os
from streamlit_stl import stl_viewer

# 1. Seite & Design
st.set_page_config(page_title="3D-Print Calc & Order", page_icon="💰", layout="wide")

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
st.sidebar.header("🔧 Druck-Optionen")
wahl = st.sidebar.selectbox("Wähle dein Material:", list(material_daten.keys()))
infill = st.sidebar.select_slider("Füllung (Infill):", options=[15, 40, 70, 100], value=40)

# 4. Datei Upload
file = st.file_uploader("STL-Datei hier hochladen", type=["stl"])

if file:
    # Temporäre Datei speichern
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
        tmp.write(file.getvalue())
        tmp_path = tmp.name

    try:
        # Modell laden für Berechnung
        mesh = trimesh.load(tmp_path)
        volumen_netto = mesh.volume / 1000  
        effektive_fullung = (infill / 100) + 0.15 
        gewicht = volumen_netto * material_daten[wahl]["dichte"] * effektive_fullung
        total = gewicht * material_daten[wahl]["preis_per_g"]
        if total < 5.0: total = 5.0

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📦 3D-Vorschau")
            # --- HIER IST DER VIEWER ---
            stl_viewer(tmp_path, color="#FF4B4B") 
            st.caption("Du kannst das Modell mit der Maus drehen und zoomen.")

        with col2:
            st.subheader("💰 Dein Angebot")
            st.success(f"### Preis: {total:.2f} €")
            st.write(f"**Gewicht:** ca. {gewicht:.1f} g")
            st.write(f"**Maße:** {mesh.bounding_box.extents[0]:.1f} x {mesh.bounding_box.extents[1]:.1f} x {mesh.bounding_box.extents[2]:.1f} mm")
            
            st.divider()
            nachricht = f"Hallo Gian, ich möchte '{file.name}' drucken lassen. Material: {wahl}, Infill: {infill}%. Preis: {total:.2f}€."
            mailto = f"mailto:mixmasteringbyg@gmail.com?subject=Anfrage: {file.name}&body={nachricht}"
            whatsapp = f"https://wa.me/4915563398574?text={nachricht.replace(' ', '%20')}"

            c_mail, c_wa = st.columns(2)
            c_mail.markdown(f'<a href="{mailto}" style="text-decoration:none;"><div style="background-color:#ff4b4b;color:white;padding:12px;border-radius:10px;text-align:center;font-weight:bold;">📩 E-Mail</div></a>', unsafe_allow_html=True)
            c_wa.markdown(f'<a href="{whatsapp}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:12px;border-radius:10px;text-align:center;font-weight:bold;">💬 WhatsApp</div></a>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Fehler bei der Modell-Analyse: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# 5. Impressum & Datenschutz (Dein Original)
st.divider()
with st.expander("Rechtliche Informationen (Impressum & Datenschutz)"):
    st.markdown("""
    ### Impressum
    **Angaben gemäß § 5 DDG:** Andrea Giancarlo Sedda  
    Mix Mastering By G | c/o Smartservices GmbH | Südstraße 31 | 47475 Kamp-Lintfort  
    ... (Rest deines Textes) ...
    """)
