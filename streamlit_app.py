import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="Πωλήσεις ανά Κατάστημα", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-color: #2c3e50 !important;
    }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

excel_path = "tv sat sales.xlsx"

with st.expander("⚙️ Διαχείριση Αρχείου (Admin)"):
    password = st.text_input("Εισάγετε κωδικό διαχειριστή:", type="password")
    if password == "2845":
        uploaded_file = st.file_uploader("Επιλέξτε ή σύρετε το νέο αρχείο 'tv sat sales.xlsx':", type=["xlsx"])
        if uploaded_file is not None:
            with open(excel_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("Το αρχείο ενημερώθηκε επιτυχώς! Γίνεται ανανέωση...")
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

try:
    df = load_data()
    
    custom_title = "ΕΙΔΟΣ"
    
    if not df.empty:
        for i in range(min(3, len(df))):
            val = str(df.iloc[i, 0]).strip()
            if val and val.lower() != 'nan' and not "κατάστημα" in val.lower() and not "ποσοτ" in val.lower():
                custom_title = val
                break

        df = df.iloc[:, [0, 1]]
        df.columns = ['Κατάστημα', 'Ποσότητα']
        
        df = df.dropna(subset=['Κατάστημα', 'Ποσότητα'])
        df['Κατάστημα'] = df['Κατάστημα'].astype(str).str.strip()
        
        df = df[~df['Κατάστημα'].str.contains("Κατάστημα|ΠΟΣΟΤ|ΠΑΡΑΔΕΙΓΜΑ", case=False, na=False)]
        
        df_clean = df[~df['Κατάστημα'].str.contains("Total|Συνολο|ΣΥΝΟΛΟ", case=False, na=False)].copy()
        
        df_clean['Num_Sales'] = pd.to_numeric(df_clean['Ποσότητα'], errors='coerce').fillna(0).astype(int)
        
        total_sum = df_clean['Num_Sales'].sum()
        
        df_stores = df_clean.sort_values(by='Num_Sales', ascending=False)
        
        total_row = pd.DataFrame([{'Κατάστημα': 'TOTAL', 'Ποσότητα': total_sum, 'Num_Sales': total_sum}])
        
        df = pd.concat([df_stores, total_row], ignore_index=True)
        
        max_sales = df_stores['Num_Sales'].max() if not df_stores.empty else 1
    else:
        max_sales = 1

    html_content = f"""
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    <style>
    @keyframes blink-number-slow {{
        0% {{ opacity: 1; color: #2ecc71; text-shadow: 0 0 12px rgba(46, 204, 113, 0.7); }}
        50% {{ opacity: 0.25; color: #27ae60; text-shadow: none; }}
        100% {{ opacity: 1; color: #2ecc71; text-shadow: 0 0 12px rgba(46, 204, 113, 0.7); }}
    }}

    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 10px; background: transparent; }}
    
    .main-container {{ 
        position: relative;
        background: rgba(0, 0, 0, 0.6); 
        padding: 25px; 
        border-radius: 15px; 
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); 
        backdrop-filter: blur(8px); 
        -webkit-backdrop-filter: blur(8px); 
        max-width: 450px; 
        margin: auto; 
        text-align: center; 
    }}
    
    .top-right-text {{
        position: absolute;
        top: 15px;
        right: 18px;
        color: #3498db;
        font-size: 15px;
        font-weight: bold;
        letter-spacing: 1px;
        text-transform: uppercase;
    }}

    .main-title {{ color: white; font-size: 32px; font-weight: bold; margin-bottom: 5px; margin-top: 10px; }}
    .tv-big {{ color: white; font-size: 38px; font-weight: bold; margin-bottom: 25px; letter-spacing: 2px; }}
    .sub-title {{ color: #3498db; font-size: 16px; margin-bottom: 5px; font-weight: bold; text-transform: uppercase; }}
    
    .poll-item {{ background: rgba(255, 255, 255, 0.08); padding: 12px 18px; border-radius: 12px; margin-bottom: 12px; text-align: left; border: 1px solid rgba(255, 255, 255, 0.1); }}
    
    .poll-info {{ display: flex; justify-content: space-between; align-items: flex-start; color: white; font-size: 15px; font-weight: 500; margin-bottom: 8px; gap: 10px; }}
    .poll-info span:first-child {{ word-break: break-word; overflow-wrap: break-word; flex: 1; }}
    .poll-info span:last-child {{ white-space: nowrap; text-align: right; flex-shrink: 0; }}
    
    .win-number-first {{
        color: #2ecc71;
        animation: blink-number-slow 2.5s infinite ease-in-out;
        font-weight: bold;
    }}

    .progress-bar-bg {{ background: rgba(255, 255, 255, 0.15); border-radius: 10px; height: 12px; width: 100%; overflow: hidden; }}
    .progress-fill {{ background: #3498db; height: 100%; border-radius: 10px; }}
    .total-item {{ background: rgba(52, 152, 219, 0.25); border: 1px solid #3498db; }}
    </style>
    
    <div class="main-container">
        <div class="top-right-text">ΤΟΜΕΑΣ 3</div>
        
        <!-- ΣΤΑΘΕΡΟ LOGO ΧΩΡΙΣ ΚΙΝΗΣΗ -->
        <div style="text-align: center; margin-bottom: 15px;">
            <img src="https://raw.githubusercontent.com/tosoun/gdp-dashboard/main/unnamed-removebg-preview.png" alt="Logo" style="max-width: 90px; height: auto;">
        </div>
        <!-- --------------------------- -->
    """
    
    html_content += f'<div class="main-title">ΠΩΛΗΣΕΙΣ</div><div class="tv-big">TV</div><div class="sub-title">{custom_title}</div>'
    
    if not df.empty:
        for index, row in df.iterrows():
            katastima = str(row['Κατάστημα'])
            if katastima.lower() == 'nan' or not katastima.strip():
                continue
            num = int(row['Num_Sales'])
            formatted_num = f"{num:,}".replace(',', '.')
            bar_width = round((num / max_sales) * 100) if max_sales > 0 else 0
            if bar_width > 100: bar_width = 100
            
            is_tot_row = "total" in katastima.lower() or "σύνολο" in katastima.lower()
            
            if is_tot_row:
                html_content += f"""
                <div class="poll-item total-item">
                    <div class="poll-info">
                        <span><b>{katastima}</b></span>
                        <span><b>{formatted_num} τμχ/κιλ</b></span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-fill" style="width: {bar_width}%;"></div>
                    </div>
                </div>
                """
            elif index == 0:
                html_content += f"""
                <div class="poll-item" id="first-store-card">
                    <div class="poll-info">
                        <span><b>{katastima}</b></span>
                        <span class="win-number-first">{formatted_num} τμχ/κιλ</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-fill" style="width: {bar_width}%;"></div>
                    </div>
                </div>
                <script>
                    setTimeout(function() {{
                        const card = document.getElementById('first-store-card');
                        if(card) {{
                            const rect = card.getBoundingClientRect();
                            const x = (rect.left + rect.width / 2) / window.innerWidth;
                            const y = (rect.top + rect.height / 2) / window.innerHeight;
                            
                            const triggerConfetti = () => {{
                                confetti({{
                                    particleCount: 100,
                                    spread: 80,
                                    origin: {{ x: x, y: y }}
                                }});
                            }};

                            triggerConfetti();
                            setTimeout(triggerConfetti, 3000);
                        }}
                    }}, 300);
                </script>
                """
            else:
                html_content += f"""
                <div class="poll-item">
                    <div class="poll-info">
                        <span><b>{katastima}</b></span>
                        <span><b>{formatted_num} τμχ/κιλ</b></span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-fill" style="width: {bar_width}%;"></div>
                    </div>
                </div>
                """
    else:
        html_content += '<div style="color: white; padding: 20px;">Δεν βρέθηκαν δεδομένα στο αρχείο Excel.</div>'
    
    html_content += '</div>'
    components.html(html_content, height=1050, scrolling=True)
except Exception as e:
    st.error(f"Σφάλμα: {e}")
