from flask import Flask, jsonify
from sqlalchemy import text
from database import engine

app = Flask(__name__)

@app.get("/hello")
def hello():
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS healthcheck (id INTEGER)"))
        conn.execute(text("INSERT INTO healthcheck (id) VALUES (1)"))
        val = conn.execute(text("SELECT COUNT(*) FROM healthcheck")).scalar()

    return jsonify({"message": "Hello Fiverr", "db": "sqlite", "rows_in_healthcheck": val})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
