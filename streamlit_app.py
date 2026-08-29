import os
import sys
import pandas as pd

# Διασφάλιση υποστήριξης ελληνικών χαρακτήρων στην κονσόλα (Windows/Linux)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Δυναμικός εντοπισμός διαδρομής αρχείου στον τρέχοντα φάκελο
current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
excel_path = os.path.join(current_dir, "S3 - Πωλήσεις Ειδών-1.xlsx")

def load_and_process_sales():
    # Εναλλακτική αναζήτηση αρχείου τοπικά αν δεν το βρει απευθείας
    target_path = excel_path
    if not os.path.exists(target_path):
        target_path = "S3 - Πωλήσεις Ειδών-1.xlsx"
        if not os.path.exists(target_path):
            print(f"Σφάλμα: Δεν βρέθηκε το αρχείο Excel στη διαδρομή: {target_path}")
            return None

    try:
        # Ανάγνωση φύλλων εργασίας για έλεγχο
        xls = pd.ExcelFile(target_path)
        print(f"Επιτυχής εντοπισμός αρχείου. Διαθέσιμα φύλλα: {xls.sheet_names}")
        
        # Ανάγνωση του φύλλου 'Export'
        df = pd.read_excel(target_path, sheet_name='Export')
        
        # Έλεγχος ύπαρξης των απαραίτητων στηλών
        if 'Κατάστημα' not in df.columns or 'ΠΟΣΟΤΗΤΕΣ' not in df.columns:
            print("Σφάλμα: Οι αναμενόμενες στήλες 'Κατάστημα' ή 'ΠΟΣΟΤΗΤΕΣ' δεν βρέθηκαν στο φύλλο.")
            print(f"Υπάρχουσες στήλες: {list(df.columns)}")
            return None
        
        # Καθαρισμός δεδομένων: Αφαίρεση κενών γραμμών
        df_clean = df.dropna(subset=['Κατάστημα']).copy()
        
        # Αποκλεισμός γραμμών 'Total' και γραμμών περιγραφής φίλτρων
        mask = df_clean['Κατάστημα'].astype(str).str.contains("Total|Φίλτρα", case=False, na=False)
        df_clean = df_clean[~mask]
        
        # Κράτημα αποκλειστικά των στηλών Καταστήματος και Ποσοτήτων
        df_stores = df_clean[['Κατάστημα', 'ΠΟΣΟΤΗΤΕΣ']].copy()
        
        # Μετατροπή τιμών σε αριθμητικές και διαχείριση τυχόν σφαλμάτων
        df_stores['ΠΟΣΟΤΗΤΕΣ'] = pd.to_numeric(df_stores['ΠΟΣΟΤΗΤΕΣ'], errors='coerce').fillna(0)
        
        # Ταξινόμηση κατά φθίνουσα σειρά (από τη μεγαλύτερη ποσότητα στη μικρότερη)
        df_stores = df_stores.sort_values(by='ΠΟΣΟΤΗΤΕΣ', ascending=False).reset_index(drop=True)
        
        return df_stores

    except Exception as e:
        print(f"Παρουσιάστηκε απρόσμενο σφάλμα κατά την ανάγνωση του αρχείου: {e}")
        return None

if __name__ == "__main__":
    result_df = load_and_process_sales()
    
    if result_df is not None and not result_df.empty:
        total_quantity = result_df['ΠΟΣΟΤΗΤΕΣ'].sum()
        
        print("\n" + "="*45)
        print("     ΑΝΑΛΥΣΗ ΠΩΛΗΣΕΩΝ ΑΝΑ ΚΑΤΑΣΤΗΜΑ")
        print("="*45)
        print(f"Συνολική Ποσότητα: {total_quantity:.2f}\n")
        print(result_df.to_string(index=False))
        print("="*45)
    else:
        print("Δεν βρέθηκαν δεδομένα προς εμφάνιση.")
