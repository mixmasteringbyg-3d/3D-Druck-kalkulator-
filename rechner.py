import streamlit as st

# --- KONFIGURATION ---
st.set_page_config(page_title="Wartungsarbeiten - 3D-Print Calc", page_icon="🛠️", layout="centered")

# Modernes Design für die Wartungsseite
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .maintenance-container {
        text-align: center;
        padding: 50px;
        background-color: #1e1e1e;
        border-radius: 20px;
        border: 2px solid #25D366;
        margin-top: 50px;
    }
    .contact-link {
        color: #25D366;
        text-decoration: none;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- WARTUNGS-UI ---
st.markdown("""
    <div class="maintenance-container">
        <h1 style="color: white;">🛠️ Wartungsarbeiten</h1>
        <p style="color: #ccc; font-size: 1.2rem;">
            Wir optimieren gerade unseren 3D-Druck Kalkulator für Sie. 
            In Kürze sind wir mit verbesserten Funktionen wieder zurück!
        </p>
        <hr style="border-color: #333;">
        <p style="color: white;">
            <b>Sie haben eine dringende Anfrage?</b><br>
            Schreiben Sie uns direkt per WhatsApp oder E-Mail:
        </p>
        <p>
            💬 <a href="https://wa.me/4915563398574" class="contact-link">WhatsApp: +49 155 63398574</a><br>
            ✉️ <a href="mailto:mixmasteringbyg@gmail.com" class="contact-link">mixmasteringbyg@gmail.com</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- RECHTLICHES (Muss auch im Wartungsmodus bleiben) ---
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
    ### Datenschutzerklärung
    Auf dieser Wartungsseite werden keine personenbezogenen Daten erhoben. Bei Kontaktaufnahme via WhatsApp oder E-Mail gelten die Datenschutzbestimmungen der jeweiligen Anbieter.
    """)
