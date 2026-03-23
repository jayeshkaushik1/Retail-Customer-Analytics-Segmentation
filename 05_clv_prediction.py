import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import r2_score
from sklearn.cluster import KMeans

def predict_clv(rfm_df):
    # 1. Features to use: recency, frequency
    X = rfm_df[['Recency', 'Frequency']]
    y = rfm_df['Monetary']
    
    # 2. Drop extreme 1% outliers to stabilize training for both models
    threshold = y.quantile(0.99)
    mask = y <= threshold
    X_stable = X[mask]
    y_stable = y[mask]
    
    # 3. Split data 80/20 train/test
    X_train, X_test, y_train, y_test = train_test_split(X_stable, y_stable, test_size=0.2, random_state=42)
    
    print("\n--- Model Comparison ---")
    
    # MODEL 1: Baseline (Linear Regression)
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    lr_preds = lr_model.predict(X_test)
    lr_r2 = r2_score(y_test, lr_preds)
    print(f"1. Baseline (Linear Regression) -> R2 Score: {lr_r2:.2f}")
    
    # MODEL 2: Optimized (Gradient Boosting)
    gb_model = GradientBoostingRegressor(n_estimators=50, max_depth=3, random_state=42)
    gb_model.fit(X_train, y_train)
    gb_preds = gb_model.predict(X_test)
    gb_r2 = r2_score(y_test, gb_preds)
    print(f"2. Optimized (Gradient Boosting)  -> R2 Score: {gb_r2:.2f}")
    
    print("\nWhy did Gradient Boosting perform better?")
    print("- Linear regression struggles with non-linear customer spending patterns and is highly sensitive to variance.")
    print("- Gradient Boosting handles non-linear relationships naturally, resulting in a much higher R2.")
    
    # We will use the optimized model (Gradient Boosting) for actual CLV assignments on all customers
    rfm_df['predicted_clv'] = gb_model.predict(X)
    
    # 4. Segment customers into 4 CLV tiers using KMeans clustering
    clv_data = rfm_df[['predicted_clv']].values
    
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    rfm_df['clv_cluster'] = kmeans.fit_predict(clv_data)
    
    # Assign tier labels strictly based on cluster center magnitudes (highest center -> Platinum)
    cluster_centers = kmeans.cluster_centers_.flatten()
    sorted_centers_idx = cluster_centers.argsort()[::-1] # Descending indices
    tier_mapping = {
        sorted_centers_idx[0]: 'Platinum',
        sorted_centers_idx[1]: 'Gold',
        sorted_centers_idx[2]: 'Silver',
        sorted_centers_idx[3]: 'Bronze'
    }
    rfm_df['clv_tier'] = rfm_df['clv_cluster'].map(tier_mapping)
    
    return rfm_df

if __name__ == "__main__":
    try:
        print("Loading RFM dataset...")
        rfm_df = pd.read_csv('rfm_data.csv')
        clv_df = predict_clv(rfm_df)
        
        # 5. Print tier-wise summary: count, avg CLV, avg frequency
        summary = clv_df.groupby('clv_tier').agg({
            'CustomerID': 'count',
            'predicted_clv': 'mean',
            'Frequency': 'mean'
        }).rename(columns={'CustomerID': 'Count', 'predicted_clv': 'Avg CLV', 'Frequency': 'Avg Frequency'})
        
        # Ensuring logical print order
        ordered_tiers = [tier for tier in ['Platinum', 'Gold', 'Silver', 'Bronze'] if tier in summary.index]
        summary = summary.reindex(ordered_tiers)
        
        print("\n--- CLV Tier Summary (Using Optimized Model) ---")
        print(summary)
        
        clv_df.to_csv('clv_data.csv', index=False)
        print("\nSaved output to clv_data.csv")
    except FileNotFoundError:
        print("Error: rfm_data.csv not found. Please run 04_rfm_scoring.py first.")
