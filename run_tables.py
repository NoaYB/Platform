from models import Base, Link, Click, MonthlyStat
from database import engine

# Create the tables
Base.metadata.create_all(engine)
print("Tables created successfully!")
print(f"Models loaded: Link, Click, MonthlyStat")
print(f"Engine URL: {engine.url}")
print(f"Tables defined in models: {', '.join(Base.metadata.tables.keys())}")

# Show actual tables in the database
from sqlalchemy import inspect
inspector = inspect(engine)
print(f"\nActual tables in database: {', '.join(inspector.get_table_names())}")