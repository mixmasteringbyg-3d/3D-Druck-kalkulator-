import streamlit as st
import trimesh
import tempfile
import os

# --- 1. KONFIGURATION ---
MY_EMAIL = "mixmasteringbyg@gmail.com"
MY_PHONE = "4915563398574"

st.set_page_config(page_title="3D-Print Calc", page_icon="💰", layout="centered")

# Modernes Design (Dein Style: Dunkel mit Neon-Akzenten)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .price-box {
        padding: 20px;
        background-color: #1e1e1e;
        border-radius: 15px;
        border-left: 5px solid #25D366;
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .contact-button {
        display: block;
        padding: 18px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        text-decoration: none;
        margin-bottom: 12px;
        transition: 0.3s ease;
        font-size: 1.1rem;
    }
    .whatsapp-btn { background-color: #25D366; color: white !important; }
    .mail-btn { background-color: #0078D4; color: white !important; }
    .whatsapp-btn:hover, .mail-btn:hover { opacity: 0.9; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- HAUPTBEREICH ---
st.title("🚀 3D-Druck Preis-Kalkulator")
st.markdown("Berechnen Sie sofort den Preis für Ihr 3D-Modell.")

material_daten = {
    "PLA (Standard)": {"preis_per_g": 0.15, "dichte": 1.25},
    "PETG (Stabil)": {"preis_per_g": 0.22, "dichte": 1.27},
    "PC (Polycarbonat)": {"preis_per_g": 0.45, "dichte": 1.20}
}

st.subheader("⚙️ 1. Konfiguration")
col_a, col_b = st.columns(2)
with col_a:
    wahl = st.selectbox("Material wählen:", list(material_daten.keys()))
with col_b:
    infill = st.select_slider("Füllung (Infill %):", options=[15, 40, 70, 100], value=40)

st.divider()

st.subheader("📂 2. Modell analysieren")
uploaded_file = st.file_uploader("STL-Datei auswählen", type=["stl"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        # 3D-Analyse
        mesh = trimesh.load(tmp_path)
        volumen_netto = mesh.volume / 1000
        effektive_fullung = (infill / 100) + 0.15
        gewicht = volumen_netto * material_daten[wahl]["dichte"] * effektive_fullung
        total = max(5.0, gewicht * material_daten[wahl]["preis_per_g"])

        # Preis-Anzeige
        st.markdown(f"""
            <div class="price-box">
                <h2 style="color:white; margin:0;">Kalkulierter Preis: {total:.2f} €</h2>
                <p style="color:#888;">Modell: {uploaded_file.name} | ca. {gewicht:.1f}g</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📩 3. Jetzt bestellen")
        st.write("Bitte wählen Sie eine Kontaktmöglichkeit. Sie können die Datei dann einfach im Anhang mitsenden.")

        # Nachrichtentext für WhatsApp & Mail
        anfrage_text = (f"Hallo Gian, ich habe folgendes Modell kalkuliert: '{uploaded_file.name}'. "
                        f"Preis: {total:.2f}€, Material: {wahl}, Infill: {infill}%.")
        
        wa_link = f"https://wa.me/{MY_PHONE}?text={anfrage_text.replace(' ', '%20')}"
        mail_link = f"mailto:{MY_EMAIL}?subject=3D-Druck%20Anfrage&body={anfrage_text.replace(' ', '%20')}"
        
        # Kontakt Buttons
        st.markdown(f"""
            <a href="{wa_link}" target="_blank" class="contact-button whatsapp-btn">💬 Bestellung via WhatsApp abschließen</a>
            <a href="{mail_link}" class="contact-button mail-btn">✉️ Bestellung via E-Mail abschließen</a>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Fehler bei der Analyse: Das Modell konnte nicht gelesen werden.")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# --- VOLLSTÄNDIGES IMPRESSUM (RECHTSSICHER) ---
st.divider()
with st.expander("⚖️ Impressum & Datenschutz"):
    st.markdown("""
    ### Impressum
    **Angaben gemäß § 5 DDG:** Andrea Giancarlo Sedda  
    Mix Mastering By G | c/o Smartservices GmbH | Südstraße 31 | 47475 Kamp-Lintfort  
    **Kontakt:** E-Mail: mixmasteringbyg@gmail.com | Telefon: +49 155 63398574  
    **Umsatzsteuer:** Gemäß § 19 UStG wird keine Umsatzsteuer berechnet (Kleingewerberegelung).  
    **Verantwortlich:** Andrea Giancarlo Sedda  

    ---

    ### Urheberrecht & Haftung
    Der Nutzer versichert, dass er alle Rechte an den hochgeladenen Dateien besitzt. Mix Mastering By G führt keine Prüfung auf Markenrechtsverletzungen durch. Mit dem Absenden einer Anfrage stellt der Nutzer den Betreiber von allen Ansprüchen Dritter frei.

    ---

    ### Datenschutzerklärung
    **1. Datenerfassung:** Die Analyse Ihrer STL-Dateien erfolgt temporär im Arbeitsspeicher (RAM) und wird nach der Sitzung gelöscht. Es erfolgt keine dauerhafte Speicherung auf unseren Servern.  
    **2. Kontakt:** Erst wenn Sie aktiv auf einen der Bestell-Buttons klicken, werden Daten (Name des Modells, Preis, Material) an WhatsApp oder Ihren E-Mail-Provider übermittelt.
    """)
