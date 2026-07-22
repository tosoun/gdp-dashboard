import streamlit as st
import pandas as pd
import os
import base64
import streamlit.components.v1 as components

# 1. Ρύθμιση της σελίδας
st.set_page_config(page_title="Πωλήσεις ανά Κατάστημα", layout="centered")

# 2. Το οπτικό κομμάτι (CSS) για το σκέτο γκρι φόντο
st.markdown("""
    <style>
    .stApp {
        background-color: #2c3e50 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Φόρτωση και Υπολογισμός Δεδομένων
excel_filename = "sales_stores.xlsx"
logo_filename = "logo.png"

# Συνάρτηση για τη μετατροπή της τοπικής εικόνας σε μορφή που διαβάζει το HTML
def get_base64_image(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

logo_base64 = get_base64_image(logo_filename)

if os.path.exists(excel_filename):
    try:
        # Διάβασμα αρχείου
        df = pd.read_excel(excel_filename)
        
        # Έλεγχος αν υπάρχουν οι βασικές στήλες
        if 'Κατάστημα' in df.columns and 'Πωλήσεις' in df.columns:
            
            # Μετατροπή σε αριθμητικά δεδομένα
            df['Πωλήσεις'] = pd.to_numeric(df['Πωλήσεις'], errors='coerce').fillna(0)
            
            # Ταξινόμηση (οι περισσότερες πωλήσεις πάνω-πάνω)
            df = df.sort_values(by='Πωλήσεις', ascending=False)
            
            # Εύρεση της μέγιστης τιμής για τη μπάρα
            max_sales = df['Πωλήσεις'].max()
            
            # Χτίσιμο του πλήρους HTML και CSS μαζί
            html_content = """
            <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                margin: 0;
                padding: 10px;
                background: transparent;
            }
            .main-container {
                background: rgba(0, 0, 0, 0.6);
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
                backdrop-filter: blur(8px);
                -webkit-backdrop-filter: blur(8px);
                max-width: 450px;
                margin: auto;
                text-align: center;
            }
            .logo-container {
                margin-bottom: 15px;
            }
            .logo-img {
                max-width: 180px;
                height: auto;
            }
            .main-title {
                color: white;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            .sub-title {
                color: #3498db;
                font-size: 16px;
                margin-bottom: 25px;
                font-weight: bold;
                text-transform: uppercase;
            }
            .poll-item {
                background: rgba(255, 255, 255, 0.08);
                padding: 12px 18px;
                border-radius: 12px;
                margin-bottom: 12px;
                text-align: left;
            }
            .poll-info {
                display: flex;
                justify-content: space-between;
                color: white;
                font-size: 15px;
                font-weight: 500;
                margin-bottom: 8px;
            }
            .progress-bar-bg {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 10px;
                height: 12px;
                width: 100%;
                overflow: hidden;
            }
            .progress-fill {
                background: #3498db;
                height: 100%;
                border-radius: 10px;
            }
            </style>
            
            <div class="main-container">
            """
            
            # Προσθήκη του Logo αν υπάρχει στον φάκελο
            if logo_base64:
                html_content += f"""
                <div class="logo-container">
                    <img src="data:image/png;base64,{logo_base64}" class="logo-img" alt="Logo">
                </div>
                """
                
            html_content += """
                <div class="main-title">Αποτελέσματα Πωλήσεων</div>
                <div class="sub-title">TV ΣΠΑΜΕ ΤΙΣ ΤΙΜΕΣ</div>
            """
            
            # Δημιουργία των γραμμών
            for index, row in df.iterrows():
                katastima = row['Κατάστημα']
                posotita = row['Πωλήσεις']
                
                monada = "τεμ./κιλά"
                
                # Μορφοποίηση αριθμού
                if float(posotita).is_integer():
                    posotita_formatted = f"{int(posotita):,}"
                else:
                    posotita_formatted = f"{posotita:.3f}".rstrip('0').rstrip('.')
                    posotita_formatted = posotita_formatted.replace('.', ',')
                
                # Υπολογισμός του πλάτους της μπάρας αναλογικά με το max
                bar_width = round((posotita / max_sales) * 100) if max_sales > 0 else 0
                
                html_content += f"""
                <div class="poll-item">
                    <div class="poll-info">
                        <span>{katastima}</span>
                        <span>{posotita_formatted} {monada}</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-fill" style="width: {bar_width}%;"></div>
                    </div>
                </div>
                """
            
            html_content += '</div>'
            
            # Εμφάνιση του πίνακα
            components.html(html_content, height=950, scrolling=True)
            
        else:
            st.error("Το Excel πρέπει να έχει ακριβώς τις στήλες 'Κατάστημα' και 'Πωλήσεις'.")
    except Exception as e:
        st.error(f"Παρουσιάστηκε σφάλμα κατά την ανάγνωση: {e}")
else:
    st.info(f"Το αρχείο '{excel_filename}' δεν βρέθηκε στον φάκελο.")