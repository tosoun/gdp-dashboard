import os
import pandas as pd

# Ορισμός διαδρομής αρχείου
excel_path = "S3 - Πωλήσεις Ειδών-1.xlsx"

def load_and_process_sales():
    if not os.path.exists(excel_path):
        print(f"Το αρχείο '{excel_path}' δεν βρέθηκε.")
        return None

    try:
        # Ανάγνωση του φύλλου 'Export' του Excel
        df = pd.read_excel(excel_path, sheet_name='Export')
        
        # Καθαρισμός: Αφαίρεση κενών γραμμών στη στήλη 'Κατάστημα'
        df_clean = df.dropna(subset=['Κατάστημα']).copy()
        
        # Αποκλεισμός γραμμών που περιέχουν 'Total' ή πληροφορίες φίλτρων στο τέλος
        df_clean = df_clean[~df_clean['Κατάστημα'].astype(str).str.contains("Total|Φίλτρα", case=False, na=False)]
        
        # Επιλογή βασικών στηλών ('Κατάστημα' και 'ΠΟΣΟΤΗΤΕΣ')
        df_stores = df_clean[['Κατάστημα', 'ΠΟΣΟΤΗΤΕΣ']].copy()
        
        # Μετατροπή της ποσότητας σε αριθμητική μορφή
        df_stores['ΠΟΣΟΤΗΤΕΣ'] = pd.to_numeric(df_stores['ΠΟΣΟΤΗΤΕΣ'], errors='coerce').fillna(0)
        
        # Ταξινόμηση κατά φθίνουσα σειρά ποσότητας
        df_stores = df_stores.sort_values(by='ΠΟΣΟΤΗΤΕΣ', ascending=False).reset_index(drop=True)
        
        return df_stores
        
    except Exception as e:
        print(f"Σφάλμα κατά την επεξεργασία του αρχείου: {e}")
        return None

if __name__ == "__main__":
    df_result = load_and_process_sales()
    
    if df_result is not None and not df_result.empty:
        total_quantity = df_result['ΠΟΣΟΤΗΤΕΣ'].sum()
        
        print("=== ΑΝΑΛΥΣΗ ΠΩΛΗΣΕΩΝ ΑΝΑ ΚΑΤΑΣΤΗΜΑ ===")
        print(f"Συνολική Ποσότητα: {total_quantity:.2f}\n")
        print(df_result.to_string(index=False))
