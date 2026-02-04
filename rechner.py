import streamlit as st
import trimesh
import tempfile
import os
import smtplib
from email.message import EmailMessage

# --- 1. KONFIGURATION ---
# WICHTIG: Erstelle ein "App-Passwort" in deinem Google Account (nicht dein normales PW!)
EMAIL_SENDER = "mixmasteringbyg@gmail.com" 
EMAIL_PASSWORD = st.secrets["email_password"] # Passwort in Streamlit Secrets hinterlegen
MY_EMAIL = "mixmasteringbyg@gmail.com"

st.set_page_config(page_title="3D-Print Calc & Order", page_icon="💰", layout="centered")

# Modernes Design
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stButton>button { width: 100%; border-radius: 15px; height: 3.5em; font-weight: bold; font-size: 1.1rem; }
    div.stButton > button:first-child { background-color: #25D366; color: white; border: none; }
    .price-box { padding: 20px; background-color: #1e1e1e; border-radius: 15px; border-left: 5px solid #25D366; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. E-Mail Versand (Alternative zu Drive)
def send_email_with_file(file_path, file_name, preis, material):
    try:
        msg = EmailMessage()
        msg['Subject'] = f"NEUER AUFTRAG: {preis}€ - {material}"
        msg['From'] = EMAIL_SENDER
        msg['To'] = MY_EMAIL
        msg.set_content(f"Moin Gian,\n\nein neuer Auftrag ist eingegangen!\n\nMaterial: {material}\nPreis: {preis}€\nDatei: {file_name}")

        with open(file_path, 'rb') as f:
            file_data = f.read()
            msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"⚠️ Mail-Fehler: {e}")
        return False

# --- HAUPTBEREICH ---
st.title("🚀 3D-Druck Preis-Kalkulator")

material_daten = {
    "PLA": {"preis_per_g": 0.15, "dichte": 1.25},
    "PETG": {"preis_per_g": 0.22, "dichte": 1.27},
    "PC (Polycarbonat)": {"preis_per_g": 0.45, "dichte": 1.20}
}

st.subheader("⚙️ 1. Konfiguration")
col_a, col_b = st.columns(2)
with col_a: wahl = st.selectbox("Material wählen:", list(material_daten.keys()))
with col_b: infill = st.select_slider("Füllung (Infill %):", options=[15, 40, 70, 100], value=40)

st.divider()
st.subheader("📂 2. Modell hochladen")
uploaded_file = st.file_uploader("Wähle deine Datei", type=["stl"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        mesh = trimesh.load(tmp_path)
        volumen_netto = mesh.volume / 1000
        effektive_fullung = (infill / 100) + 0.15
        gewicht = volumen_netto * material_daten[wahl]["dichte"] * effektive_fullung
        total = max(5.0, gewicht * material_daten[wahl]["preis_per_g"])

        st.markdown(f'<div class="price-box"><h3 style="margin:0;">💰 Preis: {total:.2f} €</h3><p style="margin:5px 0 0 0; color:#888;">{uploaded_file.name} | ca. {gewicht:.1f}g</p></div>', unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📩 3. Bestätigung & Versand")
        
        if 'sent' not in st.session_state: st.session_state.sent = False

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Datei jetzt an Gian senden"):
                with st.spinner('Wird gesendet...'):
                    if send_email_with_file(tmp_path, uploaded_file.name, f"{total:.2f}", wahl):
                        st.session_state.sent = True
                        st.balloons()
        with c2:
            if st.button("❌ Abbrechen"):
                st.session_state.sent = False
                st.warning("Abgebrochen.")

        if st.session_state.sent:
            st.success("Datei wurde per E-Mail an Gian geschickt!")
            nachricht = f"Hallo Gian, ich habe '{uploaded_file.name}' gesendet. Preis: {total:.2f}€, Material: {wahl}. Ich bestätige die Urheberrechte."
            wa_link = f"https://wa.me/4915563398574?text={nachricht.replace(' ', '%20')}"
            st.markdown(f'<a href="{wa_link}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:20px; border-radius:15px; text-align:center; font-weight:bold; font-size:18px; margin-top:20px;">💬 JETZT PER WHATSAPP BESTELLEN</div></a>', unsafe_allow_html=True)

    finally:
        if os.path.exists(tmp_path): os.remove(tmp_path)

# --- IMPRESSUM ---
st.divider()
with st.expander("⚖️ Impressum & Datenschutz"):
    st.markdown("""
    ### Impressum
    **Angaben gemäß § 5 DDG:** Andrea Giancarlo Sedda | Mix Mastering By G | c/o Smartservices GmbH | Südstraße 31 | 47475 Kamp-Lintfort  
    **Kontakt:** E-Mail: mixmasteringbyg@gmail.com | Telefon: +49 155 63398574  
    **Umsatzsteuer:** Gemäß § 19 UStG keine Umsatzsteuer (Kleingewerberegelung).  
    **Verantwortlich:** Andrea Giancarlo Sedda (Anschrift oben)  
    ---
    ### Urheberrecht & Haftung
    Nutzer versichert Rechte an Dateien. Keine Prüfung auf Markenrechte. Nutzer stellt Betreiber von Ansprüchen Dritter frei.
    ---
    ### Datenschutzerklärung
    Analyse temporär im RAM. Speicherung/Versand erfolgt erst nach Klick auf den Sende-Button per verschlüsselter E-Mail an den Betreiber.
    """)
