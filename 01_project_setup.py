import pandas as pd
import sqlite3

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except sqlite3.Error as err:
        print(f"Error: '{err}'")

def main():
    print("Testing connection to local SQLite database...")
    # SQLite automatically creates the file 'ecommerce_analytics.db' locally without needing a server
    conn = sqlite3.connect("ecommerce_analytics.db")
    print("SQLite Database connection successful! Working locally.")
    
    # 1. Creating database schema
    create_customers_table = """
    CREATE TABLE IF NOT EXISTS customers (
        CustomerID INT PRIMARY KEY,
        Country VARCHAR(100)
    );
    """
    
    create_products_table = """
    CREATE TABLE IF NOT EXISTS products (
        StockCode VARCHAR(50) PRIMARY KEY,
        Description VARCHAR(255),
        UnitPrice DECIMAL(10, 2)
    );
    """
    
    create_orders_table = """
    CREATE TABLE IF NOT EXISTS orders (
        InvoiceNo VARCHAR(50),
        StockCode VARCHAR(50),
        CustomerID INT,
        Quantity INT,
        InvoiceDate DATETIME,
        FOREIGN KEY (CustomerID) REFERENCES customers(CustomerID),
        FOREIGN KEY (StockCode) REFERENCES products(StockCode)
    );
    """
    
    execute_query(conn, create_customers_table)
    execute_query(conn, create_products_table)
    execute_query(conn, create_orders_table)
    print("Tables 'customers', 'products', and 'orders' successfully initialized.")
    
    # 2. Loading CSV data into SQLite using Pandas
    try:
        print("Attempting to load 'online_retail.csv' (This might take a few moments)...")
        df = pd.read_csv('online_retail.csv', encoding='unicode_escape')
        
        # Clean basic structure for database loading
        df = df.dropna(subset=['CustomerID', 'Description'])
        
        # Creating Dataframes for each table
        customers_df = df[['CustomerID', 'Country']].drop_duplicates(subset=['CustomerID'])
        products_df = df[['StockCode', 'Description', 'UnitPrice']].drop_duplicates(subset=['StockCode'])
        orders_df = df[['InvoiceNo', 'StockCode', 'CustomerID', 'Quantity', 'InvoiceDate']]
        
        # Convert datetime format slightly for pure SQLite support
        orders_df = orders_df.copy()
        orders_df['InvoiceDate'] = pd.to_datetime(orders_df['InvoiceDate']).astype(str)
        
        print(f"Inserting {len(customers_df)} unique customers into SQLite database...")
        customers_df.to_sql('customers', conn, if_exists='replace', index=False)
        
        print(f"Inserting {len(products_df)} unique products into SQLite database...")
        products_df.to_sql('products', conn, if_exists='replace', index=False)
        
        print(f"Inserting {len(orders_df)} orders into SQLite database...")
        orders_df.to_sql('orders', conn, if_exists='replace', index=False)
        
        print("Data loaded to database successfully. It is saved in 'ecommerce_analytics.db'.")
    except FileNotFoundError:
        print("Warning: 'online_retail.csv' not found in the directory.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
