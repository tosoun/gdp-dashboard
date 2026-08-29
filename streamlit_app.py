import pandas as pd
import streamlit as st
import os

excel_path = "S3 - Πωλήσεις Ειδών-1.xlsx"

def load_data():
    if os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path, header=None)
            return df
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

file_time_str = "--:--"
if os.path.exists("time.txt"):
    try:
        with open("time.txt", "r", encoding="utf-8") as tf:
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
        for i in range(min(10, len(df))):
            row_str = str(df.iloc[i].values).lower()
            if "κατάστημα" in row_str or "καταστημα" in row_str:
                header_row_idx = i
                break

        df = df.iloc[header_row_idx + 1:].reset_index(drop=True)
        
        store_col = 0
        qty_col = 1
        
        for col in range(len(df.columns)):
            col_vals = df.iloc[:, col].astype(str).str.lower()
            if col_vals.str.contains("κατάστημα|καταστημα", na=False).any():
                store_col = col
            elif col >= 1:
                qty_col = col

        df = df.iloc[:, [store_col, qty_col]]
        df.columns = ['Κατάστημα', 'Ποσότητα']
        
        df = df.dropna(subset=['Κατάστημα', 'Ποσότητα'])
        df['Κατάστημα'] = df['Κατάστημα'].astype(str).str.strip()
        
        df = df[~df['Κατάστημα'].str.contains("Κατάστημα|ΠΟΣΟΤ|ΠΑΡΑΔΕΙΓΜΑ|NaN", case=False, na=False)]
        
        df_clean = df[~df['Κατάστημα'].str.contains("Total|Συνολο|ΣΥΝΟΛΟ", case=False, na=False)].copy()
        
        df_clean['Num_Sales'] = (
            df_clean['Ποσότητα']
            .astype(str)
            .str.replace(' ', '', regex=False)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
        )
        df_clean['Num_Sales'] = pd.to_numeric(df_clean['Num_Sales'], errors='coerce').fillna(0).round().astype(int)
        
        total_sum = df_clean['Num_Sales'].sum()
        df_stores = df_clean.sort_values(by='Num_Sales', ascending=False)
        
        total_row = pd.DataFrame([{'Κατάστημα': 'TOTAL', 'Ποσότητα': total_sum, 'Num_Sales': total_sum}])
        df = pd.concat([df_stores, total_row], ignore_index=True)
        
        max_sales = df_stores['Num_Sales'].max() if not df_stores.empty else 1
    else:
        max_sales = 1

    st.title("Πωλήσεις ανά Κατάστημα")
    st.dataframe(df)

except Exception as e:
    st.error(f"Σφάλμα: {e}")
