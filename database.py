from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///fiverr.db"  # ייצור קובץ fiverr.db בתיקייה של הפרויקט
engine = create_engine(DATABASE_URL, future=True)
