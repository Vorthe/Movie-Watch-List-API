import os
import time
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

if not db_url:
    print("DATABASE_URL is not set!")
    exit(1)

print("Waiting for database to wake up and accept connections...")
for i in range(30):  # 30 بار تلاش (حدود 2.5 دقیقه)
    try:
        # تلاش برای اتصال ساده
        conn = psycopg2.connect(db_url, connect_timeout=5)
        conn.close()
        print("Database is fully awake and ready!")
        exit(0)
    except Exception as e:
        print(
            f"Attempt {i+1}/30 failed. Database not ready yet. Retrying in 5 seconds..."
        )
        time.sleep(5)

print("Failed to connect to database after multiple attempts.")
exit(1)
