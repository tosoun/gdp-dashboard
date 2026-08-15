import streamlit as st
import pandas as pd
import os
import datetime
import streamlit.components.v1 as components
import base64

st.set_page_config(page_title="Πωλήσεις ανά Κατάστημα", layout="centered")

# Συνάρτηση για μετατροπή εικόνας σε base64
def get_image_as_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode()}"
    return ""

img_src = get_image_as_base64("spamebanner.jpg")

st.markdown("""
    <style>
    .stApp { background-color: #2c3e50 !important; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    div[data-baseweb="select"] > div, .stRadio label p { color: white !important; }
    </style>
""", unsafe_allow_html=True)

excel_path = "tv sat sales.xlsx"
time_path = "upload_time.txt"
confetti_path = "confetti_status.txt"
cheer_path = "cheer_status.txt"

# Φόρτωση ρυθμίσεων
confetti_enabled = True
if os.path.exists(confetti_path):
    with open(confetti_path, "r", encoding="utf-8") as cf: confetti_enabled = cf.read().strip() == "True"

cheer_enabled = True
if os.path.exists(cheer_path):
    with open(cheer_path, "r", encoding="utf-8") as ch: cheer_enabled = ch.read().strip() == "True"

with st.expander("⚙️ Διαχείριση Αρχείου (Admin)"):
    password = st.text_input("Εισάγετε κωδικό διαχειριστή:", type="password")
    if password == "2845":
        uploaded_file = st.file_uploader("Επιλέξτε το 'tv sat sales.xlsx':", type=["xlsx"])
        if uploaded_file:
            with open(excel_path, "wb") as f: f.write(uploaded_file.getbuffer())
            st.success("Το αρχείο ανέβηκε!")
            st.rerun()
    elif password: st.error("Λάθος κωδικός!")

def load_data():
    return pd.read_excel(excel_path, header=None) if os.path.exists(excel_path) else pd.DataFrame()

file_time_str = "--:--"
if os.path.exists(time_path):
    with open(time_path, "r", encoding="utf-8") as tf: file_time_str = tf.read().strip()

try:
    df = load_data()
    custom_title = "ΕΙΔΟΣ"
    if not df.empty:
        # Αυτόματη εύρεση τίτλου και header
        for i in range(min(5, len(df))):
            for j in range(len(df.columns)):
                val = str(df.iloc[i, j]).strip()
                if val and val.lower() not in ['nan', 'κατάστημα', 'ποσοτητα', 'αξια']:
                    custom_title = val; break
            if custom_title != "ΕΙΔΟΣ": break
        
        header_row_idx = 0
        for i in range(min(5, len(df))):
            if "κατάστημα" in str(df.iloc[i].values).lower(): header_row_idx = i; break
        
        df.columns = df.iloc[header_row_idx]
        df = df.iloc[header_row_idx + 1:].reset_index(drop=True)
        
        # Καθαρισμός δεδομένων
        df = df.dropna(subset=[df.columns[0], df.columns[1]])
        df['Κατάστημα'] = df[df.columns[0]].astype(str)
        df['Num_Sales'] = pd.to_numeric(df[df.columns[1]].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce').fillna(0).astype(int)
        
        df_stores = df[~df['Κατάστημα'].str.contains("Total|Συνολο", case=False, na=False)].sort_values(by='Num_Sales', ascending=False)
        total_sum = df_stores['Num_Sales'].sum()
        max_sales = df_stores['Num_Sales'].max() if not df_stores.empty else 1
    else:
        max_sales = 1

    html_content = f"""
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    <style>
    .main-container {{ position: relative; background: rgba(0, 0, 0, 0.6); padding: 0; border-radius: 15px; backdrop-filter: blur(8px); max-width: 450px; margin: auto; text-align: center; overflow: hidden; }}
    .banner-image {{ width: 100%; height: 130px; object-fit: cover; display: block; }}
    .content-padding {{ padding: 25px; }}
    .top-left-area {{ position: absolute; top: 15px; left: 20px; text-align: left; z-index: 10; }}
    .top-left-text {{ color: white; font-size: 11px; font-weight: 600; text-transform: uppercase; text-shadow: 1px 1px 2px black; }}
    .pro-title {{ color: #ffffff; font-size: 30px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; }}
    .poll-item {{ background: rgba(255, 255, 255, 0.08); padding: 12px; border-radius: 10px; margin-bottom: 10px; text-align: left; }}
    .progress-fill {{ background: #3498db; height: 10px; border-radius: 5px; }}
    </style>
    <div class="main-container">
        <img src="{img_src}" class="banner-image" alt="banner">
        <div class="top-left-area">
            <div class="top-left-text">ΤΟΜΕΑΣ 3</div>
            <div style="color: #ccc; font-size: 10px;">εως: {file_time_str}</div>
        </div>
        <div class="content-padding">
            <div class="pro-title">SALES</div>
            <div style="color: #3498db; font-size: 14px; margin-bottom: 15px;">{custom_title}</div>
    """
    
    if not df.empty:
        for index, row in df_stores.iterrows():
            bar_width = round((row['Num_Sales'] / max_sales) * 100)
            html_content += f'<div class="poll-item"><div style="display:flex; justify-content:space-between; color:white;"><b>{row["Κατάστημα"]}</b><b>{row["Num_Sales"]}</b></div><div style="background:#444; height:10px; border-radius:5px; margin-top:5px;"><div class="progress-fill" style="width: {bar_width}%;"></div></div></div>'
        html_content += f'<div class="poll-item" style="border: 1px solid #3498db;"><b>ΣΥΝΟΛΟ: {total_sum}</b></div>'
    
    html_content += '</div></div>'
    components.html(html_content, height=1100)
except Exception as e:
    st.error(f"Σφάλμα: {e}")
