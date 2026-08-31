import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.join(os.getcwd(), "backend"))
load_dotenv(os.path.join(os.getcwd(), "backend", ".env"))
import psycopg2

try:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT pg_terminate_backend(8821);")
    cur.execute("SELECT pg_terminate_backend(7001);")
    print("Terminated orphaned PIDs")
    conn.close()
except Exception as e:
    print(e)
