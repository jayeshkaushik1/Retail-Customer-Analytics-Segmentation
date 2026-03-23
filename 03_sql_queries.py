import pandas as pd
import sqlite3

def run_query_to_df(query, connection):
    """Executes a query and returns the results as a Pandas DataFrame."""
    return pd.read_sql(query, connection)

def main():
    try:
        # Connecting gracefully to the local .db file without credentials!
        conn = sqlite3.connect("ecommerce_analytics.db")
    except Exception as e:
        print("Could not connect to database. Make sure 01_project_setup.py was successful.")
        return

    print("--- 1. Top 10 products by total revenue ---")
    query1 = """
    SELECT p.Description, SUM(o.Quantity * p.UnitPrice) as TotalRevenue
    FROM orders o
    JOIN products p ON o.StockCode = p.StockCode
    GROUP BY p.Description
    ORDER BY TotalRevenue DESC
    LIMIT 10;
    """
    try:
        print(run_query_to_df(query1, conn))
    except Exception as e: print("DB empty or setup failed:", e)

    print("\n--- 2. Monthly revenue trend ---")
    query2 = """
    SELECT strftime('%Y', InvoiceDate) as Year, strftime('%m', InvoiceDate) as Month, SUM(Quantity * p.UnitPrice) as Revenue
    FROM orders o 
    JOIN products p ON o.StockCode = p.StockCode
    GROUP BY Year, Month
    ORDER BY Year, Month;
    """
    try:
        print(run_query_to_df(query2, conn))
    except Exception as e: print("Query Error:", e)

    print("\n--- 3. Top 10 countries by number of orders ---")
    query3 = """
    SELECT c.Country, COUNT(DISTINCT o.InvoiceNo) as TotalOrders
    FROM orders o 
    JOIN customers c ON o.CustomerID = c.CustomerID
    GROUP BY c.Country
    ORDER BY TotalOrders DESC
    LIMIT 10;
    """
    try:
        print(run_query_to_df(query3, conn))
    except Exception: pass

    print("\n--- 4. Repeat vs New customer count ---")
    query4 = """
    WITH CustomerOrderCounts AS (
        SELECT CustomerID, COUNT(DISTINCT InvoiceNo) as OrderCount
        FROM orders
        GROUP BY CustomerID
    )
    SELECT 
        CASE WHEN OrderCount > 1 THEN 'Repeat Customer' ELSE 'New Customer' END as CustomerType,
        COUNT(*) as CustomerCount
    FROM CustomerOrderCounts
    GROUP BY CustomerType;
    """
    try:
        print(run_query_to_df(query4, conn))
    except Exception: pass

    print("\n--- 5. Average order value per country ---")
    query5 = """
    WITH OrderValues AS (
        SELECT o.InvoiceNo, c.Country, SUM(o.Quantity * p.UnitPrice) as OrderValue
        FROM orders o
        JOIN customers c ON o.CustomerID = c.CustomerID
        JOIN products p ON o.StockCode = p.StockCode
        GROUP BY o.InvoiceNo, c.Country
    )
    SELECT Country, AVG(OrderValue) as AvgOrderValue
    FROM OrderValues
    GROUP BY Country
    ORDER BY AvgOrderValue DESC;
    """
    try:
        print(run_query_to_df(query5, conn))
    except Exception: pass

    print("\n--- 6. Revenue contribution % by product category (cumulative Pareto) ---")
    query6 = """
    WITH ProductRevenue AS (
        SELECT p.Description, SUM(o.Quantity * p.UnitPrice) as Revenue
        FROM orders o JOIN products p ON o.StockCode = p.StockCode
        GROUP BY p.Description
    ),
    TotalRev AS (
        SELECT SUM(Revenue) as GrandTotal FROM ProductRevenue
    ),
    RankedProducts AS (
        SELECT Description, Revenue,
               SUM(Revenue) OVER (ORDER BY Revenue DESC) as CumulativeRevenue,
               (SUM(Revenue) OVER (ORDER BY Revenue DESC) / (SELECT GrandTotal FROM TotalRev)) * 100 as CumulativePercentage
        FROM ProductRevenue
    )
    SELECT * FROM RankedProducts LIMIT 20;
    """
    try:
        print(run_query_to_df(query6, conn))
    except Exception: pass

    print("\n--- 7. Peak shopping hours analysis ---")
    query7 = """
    SELECT strftime('%H', InvoiceDate) as ShoppingHour, COUNT(DISTINCT InvoiceNo) as TotalOrders
    FROM orders
    GROUP BY ShoppingHour
    ORDER BY TotalOrders DESC;
    """
    try:
        print(run_query_to_df(query7, conn))
    except Exception: pass

    conn.close()

if __name__ == "__main__":
    main()
