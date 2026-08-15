import streamlit as st
import pandas as pd
import os
import datetime
import streamlit.components.v1 as components
import base64

st.set_page_config(page_title="Πωλήσεις ανά Κατάστημα", layout="centered")

# Συνάρτηση για να φέρει το banner
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
    try:
        with open(confetti_path, "r", encoding="utf-8") as cf: confetti_enabled = cf.read().strip() == "True"
    except Exception: pass

cheer_enabled = True
if os.path.exists(cheer_path):
    try:
        with open(cheer_path, "r", encoding="utf-8") as ch: cheer_enabled = ch.read().strip() == "True"
    except Exception: pass

with st.expander("⚙️ Διαχείριση Αρχείου (Admin)"):
    password = st.text_input("Εισάγετε κωδικό διαχειριστή:", type="password")
    if password == "2845":
        uploaded_file = st.file_uploader("Επιλέξτε το 'tv sat sales.xlsx':", type=["xlsx"])
        time_options = [datetime.time(h, m) for h in range(24) for m in (0, 30)]
        default_time = datetime.time(datetime.datetime.now().hour, 0)
        selected_time = st.selectbox("Ώρα αναφοράς:", options=time_options, format_func=lambda x: x.strftime("%H:%M"))
        col_confetti, col_cheer = st.columns(2)
        confetti_choice = col_confetti.radio("Κομφετί:", ["ΝΑΙ", "ΟΧΙ"], index=0 if confetti_enabled else 1, horizontal=True)
        cheer_choice = col_cheer.radio("Χειροκρότημα:", ["ΝΑΙ", "ΟΧΙ"], index=0 if cheer_enabled else 1, horizontal=True)
        
        if uploaded_file is not None:
            with open(excel_path, "wb") as f: f.write(uploaded_file.getbuffer())
            with open(time_path, "w", encoding="utf-8") as tf: tf.write(selected_time.strftime("%H:%M"))
            with open(confetti_path, "w", encoding="utf-8") as cf: cf.write(str(confetti_choice == "ΝΑΙ"))
            with open(cheer_path, "w", encoding="utf-8") as ch: ch.write(str(cheer_choice == "ΝΑΙ"))
            st.success("Αποθηκεύτηκαν! Γίνεται ανανέωση..."); st.rerun()
    elif password: st.error("Λάθος κωδικός!")

def load_data():
    return pd.read_excel(excel_path, header=None) if os.path.exists(excel_path) else pd.DataFrame()

file_time_str = "--:--"
if os.path.exists(time_path):
    try:
        with open(time_path, "r", encoding="utf-8") as tf: file_time_str = tf.read().strip()
    except Exception: pass

try:
    df = load_data()
    custom_title = "ΕΙΔΟΣ"
    if not df.empty:
        # Επεξεργασία δεδομένων όπως την είχες
        for i in range(min(5, len(df))):
            for j in range(len(df.columns)):
                val = str(df.iloc[i, j]).strip()
                if val and val.lower() not in ['nan', 'κατάστημα', 'ποσοτητα', 'αξια', 'κοστος']:
                    custom_title = val; break
            if custom_title != "ΕΙΔΟΣ": break
        
        header_row_idx = 0
        for i in range(min(5, len(df))):
            if "κατάστημα" in str(df.iloc[i].values).lower(): header_row_idx = i; break
        
        df.columns = df.iloc[header_row_idx]
        df = df.iloc[header_row_idx + 1:].reset_index(drop=True)
        
        df = df.dropna(subset=[df.columns[0], df.columns[1]])
        df['Κατάστημα'] = df[df.columns[0]].astype(str).str.strip()
        df['Num_Sales'] = pd.to_numeric(df[df.columns[1]].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce').fillna(0).astype(int)
        
        df_stores = df[~df['Κατάστημα'].str.contains("Total|Συνολο", case=False, na=False)].sort_values(by='Num_Sales', ascending=False)
        total_sum = df_stores['Num_Sales'].sum()
        max_sales = df_stores['Num_Sales'].max() if not df_stores.empty else 1
    else:
        max_sales = 1

    # Εδώ είναι το HTML που διατηρεί τη δομή σου
    html_content = f"""
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    <style>
    .main-container {{ position: relative; background: rgba(0, 0, 0, 0.6); padding: 0; border-radius: 15px; backdrop-filter: blur(8px); max-width: 450px; margin: auto; text-align: center; overflow: hidden; }}
    .banner-image {{ width: 100%; height: 130px; object-fit: cover; display: block; }}
    .info-box {{ padding: 25px; }}
    .top-left-area {{ text-align: left; margin-bottom: 10px; }}
    .top-left-text {{ color: #3498db; font-size: 11px; font-weight: 600; text-transform: uppercase; }}
    .pro-title {{ color: #ffffff; font-size: 30px; font-weight: 800; text-transform: uppercase; margin-bottom: 20px; }}
    .poll-item {{ background: rgba(255, 255, 255, 0.08); padding: 12px; border-radius: 12px; margin-bottom: 10px; text-align: left; border: 1px solid rgba(255, 255, 255, 0.1); }}
    </style>
    <div class="main-container">
        <img src="{img_src}" class="banner-image" alt="banner">
        <div class="info-box">
            <div class="top-left-area">
                <div class="top-left-text">ΤΟΜΕΑΣ 3</div>
                <div style="color: #7f8c8d; font-size: 10px;">εως: {file_time_str}</div>
            </div>
            <div class="pro-title">SALES TV</div>
            <div style="color: #3498db; font-size: 15px; margin-bottom: 10px;">{custom_title}</div>
    """
    
    # Προσθήκη σειρών
    if not df.empty:
        for index, row in df_stores.iterrows():
            bar_width = round((row['Num_Sales'] / max_sales) * 100)
            html_content += f'<div class="poll-item"><div style="display:flex; justify-content:space-between; color:white;"><b>{row["Κατάστημα"]}</b><b>{row["Num_Sales"]}</b></div><div style="background:rgba(255,255,255,0.1); height:10px; border-radius:5px; margin-top:5px;"><div style="background:#3498db; height:100%; width:{bar_width}%; border-radius:5px;"></div></div></div>'
        html_content += f'<div class="poll-item" style="border:1px solid #3498db;"><b>ΣΥΝΟΛΟ: {total_sum}</b></div>'
    
    html_content += '</div></div>'
    components.html(html_content, height=1200)
except Exception as e:
    st.error(f"Σφάλμα: {e}")
