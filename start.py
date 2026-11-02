import os
import time
import subprocess
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

print("Waiting for database to wake up...")
for i in range(20):
    try:
        conn = psycopg2.connect(db_url, connect_timeout=5)
        conn.close()
        print("Database is ready!")
        break
    except Exception:
        print(f"Attempt {i+1}/20 failed. Retrying in 5s...")
        time.sleep(5)
else:
    print("Warning: Could not connect to the database. Starting app anyway...")

print("Running Alembic migrations...")
try:
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    print("Migrations completed successfully!")
except subprocess.CalledProcessError as e:
    print(f"Migration failed: {e}")

print("Starting Uvicorn server...")
os.execvp("uvicorn", ["uvicorn", "App.main:app", "--host", "0.0.0.0", "--port", "8000"])
