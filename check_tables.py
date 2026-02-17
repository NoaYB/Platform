from sqlalchemy import inspect
from database import engine

inspector = inspect(engine)
table_names = inspector.get_table_names()

print("Tables in the database:")
for table_name in table_names:
    print(f"- {table_name}")

if not table_names:
    print("No tables found in the database!")