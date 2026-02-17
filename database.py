from sqlalchemy import create_engine

# Use PostgreSQL as required
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/fiverr"

engine = create_engine(DATABASE_URL, future=True)
