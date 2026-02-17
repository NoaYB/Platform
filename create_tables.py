from models import Base
from database import engine

def create_tables():
    # Create all tables defined in models.py
    Base.metadata.create_all(engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    create_tables()