import streamlit as st
import pandas as pd
import os

# Ρύθμιση σελίδας
st.set_page_config(page_title="Πωλήσεις Ειδών", layout="wide")

st.title("📊 Ανάλυση Πωλήσεων ανά Κατάστημα")

# Ορισμός διαδρομής αρχείου
excel_path = "S3 - Πωλήσεις Ειδών-1.xlsx"

@st.cache_data
def load_and_process_sales():
    if not os.path.exists(excel_path):
        return None, "Το αρχείο Excel δεν βρέθηκε στον φάκελο."
    
    try:
        # Ανάγνωση φύλλου 'Export'
        df = pd.read_excel(excel_path, sheet_name='Export')
        
        if 'Κατάστημα' not in df.columns or 'ΠΟΣΟΤΗΤΕΣ' not in df.columns:
            return None, f"Οι αναμενόμενες στήλες δεν βρέθηκαν. Υπάρχουσες: {list(df.columns)}"
        
        # Καθαρισμός δεδομένων
        df_clean = df.dropna(subset=['Κατάστημα']).copy()
        mask = df_clean['Κατάστημα'].astype(str).str.contains("Total|Φίλτρα", case=False, na=False)
        df_clean = df_clean[~mask]
        
        df_stores = df_clean[['Κατάστημα', 'ΠΟΣΟΤΗΤΕΣ']].copy()
        df_stores['ΠΟΣΟΤΗΤΕΣ'] = pd.to_numeric(df_stores['ΠΟΣΟΤΗΤΕΣ'], errors='coerce').fillna(0)
        df_stores = df_stores.sort_values(by='ΠΟΣΟΤΗΤΕΣ', ascending=False).reset_index(drop=True)
        
        return df_stores, None
    except Exception as e:
        return None, str(e)

# Εκτέλεση και εμφάνιση
df_result, error_msg = load_and_process_sales()

if error_msg:
    st.error(f"Σφάλμα: {error_msg}")
elif df_result is not None and not df_result.empty:
    total_quantity = df_result['ΠΟΣΟΤΗΤΕΣ'].sum()
    
    # Εμφάνιση βασικής μετρικής συνόλου
    st.metric(label="Συνολική Ποσότητα", value=f"{total_quantity:,.2f}")
    
    # Εμφάνιση πίνακα δεδομένων
    st.dataframe(df_result, use_container_width=True)
else:
    st.warning("Δεν βρέθηκαν δεδομένα προς εμφάνιση.")
