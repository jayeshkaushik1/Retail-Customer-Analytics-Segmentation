import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def generate_visualizations():
    # Use clean style as requested
    sns.set_theme(style="whitegrid")
    
    try:
        cleaned_df = pd.read_csv('cleaned_online_retail.csv', parse_dates=['InvoiceDate'])
        rfm_df = pd.read_csv('clv_data.csv') 
        has_data = True
    except FileNotFoundError:
        has_data = False
        print("Target datasets not found. Please generate cleaned_online_retail.csv and clv_data.csv first.")
        
    if has_data:
        print("Generating visualisations...")
        
        # 1. Monthly revenue trend - line chart
        plt.figure(figsize=(10, 6))
        monthly_revenue = cleaned_df.set_index('InvoiceDate').resample('ME')['TotalRevenue'].sum().reset_index()
        sns.lineplot(data=monthly_revenue, x='InvoiceDate', y='TotalRevenue', marker='o')
        plt.title('Monthly Revenue Trend')
        plt.xlabel('Date')
        plt.ylabel('Total Revenue')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('01_monthly_revenue_trend.png')
        plt.close()
        print("Saved 01_monthly_revenue_trend.png")

        # 2. Top 10 products by revenue - horizontal bar chart
        plt.figure(figsize=(10, 6))
        top_products = cleaned_df.groupby('Description')['TotalRevenue'].sum().sort_values(ascending=False).head(10).reset_index()
        sns.barplot(data=top_products, x='TotalRevenue', y='Description', palette='viridis')
        plt.title('Top 10 Products by Revenue')
        plt.xlabel('Total Revenue')
        plt.ylabel('Product Description')
        plt.tight_layout()
        plt.savefig('02_top_10_products.png')
        plt.close()
        print("Saved 02_top_10_products.png")

        # 3. RFM segment distribution - pie chart
        plt.figure(figsize=(10, 6))
        segment_counts = rfm_df['Segment'].value_counts()
        plt.pie(segment_counts, labels=segment_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
        plt.title('RFM Segment Distribution')
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig('03_rfm_segments.png')
        plt.close()
        print("Saved 03_rfm_segments.png")

        # 4. CLV tier distribution - bar chart with counts
        plt.figure(figsize=(10, 6))
        ordered_tiers = [t for t in ['Platinum', 'Gold', 'Silver', 'Bronze'] if t in rfm_df['clv_tier'].unique()]
        tier_counts = rfm_df['clv_tier'].value_counts().reindex(ordered_tiers)
        
        ax = sns.barplot(x=tier_counts.index, y=tier_counts.values, palette='magma')
        for i, v in enumerate(tier_counts.values):
            if not pd.isna(v):
                ax.text(i, v + (v*0.02), str(int(v)), ha='center', va='bottom')
        plt.title('CLV Tier Distribution')
        plt.xlabel('CLV Tier')
        plt.ylabel('Number of Customers')
        plt.tight_layout()
        plt.savefig('04_clv_tiers.png')
        plt.close()
        print("Saved 04_clv_tiers.png")

        # 5. Recency vs Monetary scatter plot - colored by segment
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=rfm_df, x='Recency', y='Monetary', hue='Segment', alpha=0.7, palette='Set2')
        plt.title('Recency vs Monetary (by Segment)')
        plt.xlabel('Recency (Days)')
        plt.ylabel('Monetary Value')
        # Implementing a symlog scale for highly variable monetary values in e-commerce
        plt.yscale('symlog') 
        plt.tight_layout()
        plt.savefig('05_recency_vs_monetary.png')
        plt.close()
        print("Saved 05_recency_vs_monetary.png")

        # 6. Pareto chart - cumulative revenue % by product (80/20 rule)
        plt.figure(figsize=(10, 6))
        prod_rev = cleaned_df.groupby('Description')['TotalRevenue'].sum().sort_values(ascending=False)
        cumulative_rev_pct = (prod_rev.cumsum() / prod_rev.sum()) * 100
        
        # Plot top 100 products for Pareto shape visibility
        subset_limit = min(100, len(prod_rev))
        x = np.arange(subset_limit)
        
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        ax1.bar(x, prod_rev[:subset_limit].values, color='steelblue')
        ax1.set_ylabel('Revenue', color='steelblue')
        ax1.set_xlabel(f'Top {subset_limit} Products Ranked')
        ax1.tick_params(axis='x', bottom=False, labelbottom=False)
        
        ax2 = ax1.twinx()
        ax2.plot(x, cumulative_rev_pct[:subset_limit].values, color='darkorange', marker='.', markersize=4)
        ax2.set_ylabel('Cumulative %', color='darkorange')
        ax2.axhline(80, color='red', linestyle='--', alpha=0.5, label='80% Threshold')
        
        plt.title('Pareto Chart: Top Products vs. Revenue')
        plt.tight_layout()
        plt.savefig('06_pareto_chart.png')
        plt.close()
        print("Saved 06_pareto_chart.png")

if __name__ == "__main__":
    generate_visualizations()
