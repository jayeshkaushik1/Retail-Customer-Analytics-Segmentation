import pandas as pd
import numpy as np

def clean_ecommerce_data(file_path):
    print("Loading data...")
    df = pd.read_csv(file_path, encoding='unicode_escape')
    initial_rows = len(df)
    print(f"Initial row count: {initial_rows}")
    
    # 1. Remove rows where CustomerID or InvoiceNo is null
    df.dropna(subset=['CustomerID', 'InvoiceNo'], inplace=True)
    step1_rows = len(df)
    print(f"Removed {(initial_rows - step1_rows)} rows with null CustomerID or InvoiceNo. Remaining: {step1_rows}")
    
    # 2. Remove duplicate InvoiceNo entries
    # Removing completely duplicated rows instead of just InvoiceNo to preserve multiple items per order
    df.drop_duplicates(inplace=True)
    step2_rows = len(df)
    print(f"Removed {(step1_rows - step2_rows)} completely duplicate rows. Remaining: {step2_rows}")
    
    # 3. Remove cancelled orders (InvoiceNo starting with 'C')
    df['InvoiceNo'] = df['InvoiceNo'].astype(str)
    df = df[~df['InvoiceNo'].str.startswith('C')]
    step3_rows = len(df)
    print(f"Removed {(step2_rows - step3_rows)} cancelled orders. Remaining: {step3_rows}")
    
    # 4. Fix negative quantities and prices - remove them
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    step4_rows = len(df)
    print(f"Removed {(step3_rows - step4_rows)} rows with negative/zero quantity or price. Remaining: {step4_rows}")
    
    # 5. Convert InvoiceDate to datetime format
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # 6. Strip and lowercase the Description column
    df['Description'] = df['Description'].astype(str).str.strip().str.lower()
    
    # 7. Add a TotalRevenue column = Quantity * UnitPrice
    df['TotalRevenue'] = df['Quantity'] * df['UnitPrice']
    
    # 8. Print a cleaning summary
    print("\n--- Cleaning Summary ---")
    print(f"Total rows removed: {initial_rows - len(df)}")
    print(f"Final row count: {len(df)}")
    print("------------------------")
    
    return df

if __name__ == "__main__":
    try:
        clean_df = clean_ecommerce_data('online_retail.csv')
        clean_df.to_csv('cleaned_online_retail.csv', index=False)
        print("Saved cleaned data to cleaned_online_retail.csv")
    except FileNotFoundError:
        print("online_retail.csv not found. Please provide the dataset in the project root.")
