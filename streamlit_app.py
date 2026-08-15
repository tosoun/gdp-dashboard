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
    .stApp {
        background-color: #2c3e50 !important;
    }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    div[data-baseweb="select"] > div, .stRadio label p {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

excel_path = "tv sat sales.xlsx"
time_path = "upload_time.txt"
confetti_path = "confetti_status.txt"
cheer_path = "cheer_status.txt"

confetti_enabled = True
if os.path.exists(confetti_path):
    try:
        with open(confetti_path, "r", encoding="utf-8") as cf:
            confetti_enabled = cf.read().strip() == "True"
    except Exception:
        pass

cheer_enabled = True
if os.path.exists(cheer_path):
    try:
        with open(cheer_path, "r", encoding="utf-8") as ch:
            cheer_enabled = ch.read().strip() == "True"
    except Exception:
        pass

with st.expander("⚙️ Διαχείριση Αρχείου (Admin)"):
    password = st.text_input("Εισάγετε κωδικό διαχειριστή:", type="password")
    if password == "2845":
        uploaded_file = st.file_uploader("Επιλέξτε ή σύρετε το νέο αρχείο 'tv sat sales.xlsx':", type=["xlsx"])
        
        time_options = []
        for hour in range(24):
            for minute in (0, 30):
                time_options.append(datetime.time(hour, minute))
        
        now = datetime.datetime.now() - datetime.timedelta(hours=1)
        default_minute = 0 if now.minute < 30 else 30
        default_time = datetime.time(now.hour, default_minute)
        
        if 'selected_half_hour' not in st.session_state:
            st.session_state.selected_half_hour = default_time

        col_time, col_confetti, col_cheer = st.columns([1.2, 1, 1])
        
        with col_time:
            selected_time = st.selectbox(
                "Ώρα αναφοράς:",
                options=time_options,
                index=time_options.index(st.session_state.selected_half_hour) if st.session_state.selected_half_hour in time_options else 0,
                format_func=lambda x: x.strftime("%H:%M")
            )
            st.session_state.selected_half_hour = selected_time

        with col_confetti:
            confetti_choice = st.radio("Κομφετί:", ["ΝΑΙ", "ΟΧΙ"], index=0 if confetti_enabled else 1, horizontal=True)

        with col_cheer:
            cheer_choice = st.radio("Χειροκρότημα:", ["ΝΑΙ", "ΟΧΙ"], index=0 if cheer_enabled else 1, horizontal=True)

        if uploaded_file is not None:
            with open(excel_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        
            current_time_str = selected_time.strftime("%H:%M")
            with open(time_path, "w", encoding="utf-8") as tf:
                tf.write(current_time_str)

            with open(confetti_path, "w", encoding="utf-8") as cf:
                cf.write(str(confetti_choice == "ΝΑΙ"))

            with open(cheer_path, "w", encoding="utf-8") as ch:
                ch.write(str(cheer_choice == "ΝΑΙ"))

            st.success("Οι ρυθμίσεις αποθηκεύτηκαν αυτόματα! Γίνεται ανανέωση...")
            components.html("""
                <script>
                    setTimeout(function() {
                        window.parent.location.reload();
                    }, 1000);
                </script>
            """, height=0)
    elif password:
        st.error("Λάθος κωδικός!")

def load_data():
    if os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path, header=None)
            return df
        except Exception as e:
            return pd.DataFrame()
    return pd.DataFrame()

file_time_str = "--:--"
if os.path.exists(time_path):
    try:
        with open(time_path, "r", encoding="utf-8") as tf:
            file_time_str = tf.read().strip()
    except Exception:
        pass

try:
    df = load_data()
    custom_title = "ΕΙΔΟΣ"
    
    if not df.empty:
        for i in range(min(5, len(df))):
            for j in range(len(df.columns)):
                val = str(df.iloc[i, j]).strip()
                if val and val.lower() != 'nan' and not "κατάστημα" in val.lower() and not "πληρωτ" in val.lower() and not "ποσοτ" in val.lower() and not "αξια" in val.lower() and not "κοστος" in val.lower():
                    custom_title = val
                    break
            if custom_title != "ΕΙΔΟΣ":
                break

        header_row_idx = 0
        for i in range(min(5, len(df))):
            row_str = str(df.iloc[i].values).lower()
            if "κατάστημα" in row_str or "καταστημα" in row_str:
                header_row_idx = i
                break

        df.columns = df.iloc[header_row_idx]
        df = df.iloc[header_row_idx + 1:].reset_index(drop=True)

        col_kat, col_pos = None, None
        for col in df.columns:
            col_str = str(col).lower()
            if "κατάστημα" in col_str or "καταστημα" in col_str:
                col_kat = col
            elif "ποσοτ" in col_str:
                col_pos = col

        if col_kat is None: col_kat = df.columns[0]
        if col_pos is None: col_pos = df.columns[2] if len(df.columns) > 2 else df.columns[1]

        df = df[[col_kat, col_pos]].copy()
        df.columns = ['Κατάστημα', 'Ποσότητα']
        df = df.dropna(subset=['Κατάστημα', 'Ποσότητα'])
        df['Κατάστημα'] = df['Κατάστημα'].astype(str).str.strip()
        df = df[~df['Κατάστημα'].str.contains("Κατάστημα|ΠΟΣΟΤ|ΠΑΡΑΔΕΙΓΜΑ|NaN", case=False, na=False)]
        df_clean = df[~df['Κατάστημα'].str.contains("Total|Συνολο|ΣΥΝΟΛΟ", case=False, na=False)].copy()
        df_clean['Num_Sales'] = df_clean['Ποσότητα'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df_clean['Num_Sales'] = pd.to_numeric(df_clean['Num_Sales'], errors='coerce').fillna(0).astype(int)
        
        total_sum = df_clean['Num_Sales'].sum()
        df_stores = df_clean.sort_values(by='Num_Sales', ascending=False)
        total_row = pd.DataFrame([{'Κατάστημα': 'TOTAL', 'Ποσότητα': total_sum, 'Num_Sales': total_sum}])
        df = pd.concat([df_stores, total_row], ignore_index=True)
        max_sales = df_stores['Num_Sales'].max() if not df_stores.empty else 1
    else:
        max_sales = 1

    html_content = f"""
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&display=swap" rel="stylesheet">
    <style>
    @keyframes blink-number-slow {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.25; }} 100% {{ opacity: 1; }} }}
    body {{ font-family: 'Montserrat', sans-serif; margin: 0; padding: 10px; background: transparent; }}
    .main-container {{ position: relative; background: rgba(0, 0, 0, 0.6); padding: 25px; border-radius: 15px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); backdrop-filter: blur(8px); max-width: 450px; margin: auto; text-align: center; }}
    .corner-logo {{ position: absolute; top: 15px; right: 15px; width: 60px; height: 60px; border-radius: 8px; object-fit: cover; }}
    .top-left-area {{ position: absolute; top: 15px; left: 20px; text-align: left; }}
    .top-left-text {{ color: #3498db; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; }}
    .top-left-time {{ color: #7f8c8d; font-size: 10px; font-weight: 600; letter-spacing: 0.5px; }}
    .pro-title {{ color: #ffffff; font-size: 30px; font-weight: 800; margin-top: 5px; letter-spacing: 2px; text-transform: uppercase; }}
    .tv-big {{ color: #ffffff; font-size: 30px; font-weight: 800; margin-bottom: 20px; letter-spacing: 2px; text-transform: uppercase; }}
    .sub-title {{ color: #3498db; font-size: 15px; margin-bottom: 5px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }}
    .poll-item {{ background: rgba(255, 255, 255, 0.08); padding: 12px 18px; border-radius: 12px; margin-bottom: 12px; text-align: left; border: 1px solid rgba(255, 255, 255, 0.1); }}
    .poll-info {{ display: flex; justify-content: space-between; align-items: flex-start; color: white; font-size: 15px; font-weight: 600; gap: 10px; }}
    .win-number-first {{ color: #2ecc71; animation: blink-number-slow 2.5s infinite; font-weight: 700; }}
    .progress-bar-bg {{ background: rgba(255, 255, 255, 0.15); border-radius: 10px; height: 12px; width: 100%; overflow: hidden; margin-top: 8px; }}
    .progress-fill {{ background: #3498db; height: 100%; border-radius: 10px; }}
    .total-item {{ background: rgba(52, 152, 219, 0.25); border: 1px solid #3498db; }}
    .watermark {{ text-align: right; color: rgba(255, 255, 255, 0.2); font-size: 10px; margin-top: 15px; text-transform: uppercase; }}
    </style>
    <div class="main-container">
        <img src="{img_src}" class="corner-logo" alt="logo">
        <audio id="cheerAudio" preload="auto"><source src="https://www.myinstants.com/media/sounds/applause.mp3" type="audio/mpeg"></audio>
        <div class="top-left-area">
            <div class="top-left-text">ΤΟΜΕΑΣ 3</div>
            <div class="top-left-time">εως: {file_time_str}</div>
        </div>
    """
    
    html_content += f'<div class="pro-title">SALES</div><div class="tv-big">TV</div><div class="sub-title">{custom_title}</div>'
    
    if not df.empty:
        for index, row in df.iterrows():
            katastima = str(row['Κατάστημα'])
            num = int(row['Num_Sales'])
            formatted_num = f"{num:,}".replace(',', '.')
            bar_width = round((num / max_sales) * 100) if max_sales > 0 else 0
            
            if "total" in katastima.lower() or "σύνολο" in katastima.lower():
                html_content += f'<div class="poll-item total-item"><div class="poll-info"><span><b>{katastima}</b></span><span><b>{formatted_num}</b></span></div><div class="progress-bar-bg"><div class="progress-fill" style="width: {bar_width}%;"></div></div></div>'
            elif index == 0:
                html_content += f'<div class="poll-item" id="first-store-card"><div class="poll-info"><span><b>{katastima}</b></span><span class="win-number-first">{formatted_num}</span></div><div class="progress-bar-bg"><div class="progress-fill" style="width: {bar_width}%;"></div></div></div>'
                if confetti_enabled:
                    html_content += '<script>setTimeout(() => { confetti({particleCount: 100, spread: 80, origin: {y: 0.6}}); }, 300);</script>'
                if cheer_enabled:
                    html_content += '<script>document.getElementById("cheerAudio").play().catch(()=>{});</script>'
            else:
                html_content += f'<div class="poll-item"><div class="poll-info"><span><b>{katastima}</b></span><span><b>{formatted_num}</b></span></div><div class="progress-bar-bg"><div class="progress-fill" style="width: {bar_width}%;"></div></div></div>'
    
    html_content += '<div class="watermark">tosoun 2026</div></div>'
    components.html(html_content, height=1050, scrolling=True)
except Exception as e:
    st.error(f"Σφάλμα: {e}")
