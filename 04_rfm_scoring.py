import pandas as pd
import datetime as dt

def get_rfm_scores(df):
    # Ensure InvoiceDate is datetime type
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # 1. Calculate Recency, Frequency, Monetary
    max_date = df['InvoiceDate'].max() + dt.timedelta(days=1)
    
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (max_date - x.max()).days,
        'InvoiceNo': 'nunique',
        'TotalRevenue': 'sum'
    }).reset_index()
    
    rfm.rename(columns={
        'InvoiceDate': 'Recency',
        'InvoiceNo': 'Frequency',
        'TotalRevenue': 'Monetary'
    }, inplace=True)
    
    # 2. Score each metric 1-5 using pandas qcut (5=best)
    # Recency: lower days = higher score
    rfm['R'] = pd.qcut(rfm['Recency'], q=5, labels=[5, 4, 3, 2, 1])
    
    # Frequency: highly skewed right, using rank to handle duplicate boundary issues
    rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
    
    # Monetary: higher = higher score
    rfm['M'] = pd.qcut(rfm['Monetary'], q=5, labels=[1, 2, 3, 4, 5])
    
    # Convert back to numeric for conditionals
    rfm['R'] = rfm['R'].astype(int)
    rfm['F'] = rfm['F'].astype(int)
    rfm['M'] = rfm['M'].astype(int)
    
    rfm['rfm_score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)
    
    # 3. Create RFM segment labels
    def assign_segment(row):
        r, f, m = row['R'], row['F'], row['M']
        if r == 5 and f >= 4:
            return 'Champions'
        elif f >= 3 and m >= 3:
            return 'Loyal Customers'
        elif r <= 2 and f >= 3:
            return 'At Risk'
        elif r == 1 and f == 1:
            return 'Lost'
        elif r >= 4 and f <= 2:
            return 'Potential Loyalists'
        else:
            return 'Casual Shoppers'
            
    rfm['Segment'] = rfm.apply(assign_segment, axis=1)
    
    return rfm

if __name__ == "__main__":
    try:
        print("Loading cleaned dataset...")
        df = pd.read_csv('cleaned_online_retail.csv')
        rfm_df = get_rfm_scores(df)
        
        # 4. Print segment-wise customer count and average monetary value
        summary = rfm_df.groupby('Segment').agg({
            'CustomerID': 'count',
            'Monetary': 'mean'
        }).rename(columns={'CustomerID': 'Count', 'Monetary': 'Avg Monetary'})
        
        print("\n--- RFM Segment Summary ---")
        print(summary)
        
        rfm_df.to_csv('rfm_data.csv', index=False)
        print("\nSaved RFM data to rfm_data.csv")
    except FileNotFoundError:
        print("Error: cleaned_online_retail.csv not found. Please run 02_data_cleaning.py first.")
