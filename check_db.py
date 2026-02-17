from sqlalchemy import inspect, text
from database import engine

# Create an inspector
inspector = inspect(engine)

# Get list of all tables
tables = inspector.get_table_names()
print("\n===== DATABASE TABLES =====")
for table in tables:
    print(f"\nTable: {table}")
    # Get columns for each table
    columns = inspector.get_columns(table)
    print("  Columns:")
    for column in columns:
        print(f"    - {column['name']} ({column['type']})")

    # Get row count for each table
    with engine.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        print(f"  Row count: {count}")

print("\n===== SAMPLE DATA =====")
# Show sample data from links table
with engine.connect() as conn:
    # Check if links table exists and has data
    if 'links' in tables:
        links_data = conn.execute(text("SELECT * FROM links LIMIT 5")).fetchall()
        if links_data:
            print("\nSample links data:")
            for row in links_data:
                print(f"  - ID: {row[0]}, Short Code: {row[2]}, URL: {row[1][:50]}...")
        else:
            print("\nNo data in links table.")

    # Check if clicks table exists and has data
    if 'clicks' in tables:
        clicks_data = conn.execute(text("SELECT * FROM clicks LIMIT 5")).fetchall()
        if clicks_data:
            print("\nSample clicks data:")
            for row in clicks_data:
                print(f"  - ID: {row[0]}, Link ID: {row[1]}, Valid: {row[3]}, Rewarded: {row[4]}")
        else:
            print("\nNo data in clicks table.")