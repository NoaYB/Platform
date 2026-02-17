from sqlalchemy import inspect, text
from database import engine
from models import Base
import os

# Connection details
print("Database URL:", engine.url)
print("Working directory:", os.getcwd())

# Database tables info
inspector = inspect(engine)
schema_name = inspector.default_schema_name
print(f"Default schema: {schema_name}")

# List all schemas
print("\nAll schemas:")
schemas = inspector.get_schema_names()
for schema in schemas:
    print(f"- {schema}")

# Tables in default schema
print(f"\nTables in schema '{schema_name}':")
tables = inspector.get_table_names(schema=schema_name)
for table_name in tables:
    print(f"- {table_name}")
    print("  Columns:")
    for column in inspector.get_columns(table_name, schema=schema_name):
        print(f"    - {column['name']} ({column['type']})")

# Count rows in each table
print("\nRow counts:")
with engine.connect() as conn:
    for table_name in tables:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
        print(f"- {table_name}: {count} rows")

print("\nExpected tables from models.py:")
for cls in Base.__subclasses__():
    print(f"- {cls.__tablename__}")