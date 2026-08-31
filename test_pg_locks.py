import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.join(os.getcwd(), "backend"))
load_dotenv(os.path.join(os.getcwd(), "backend", ".env"))
import psycopg2

try:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("""
        SELECT pid, state, query, wait_event_type, wait_event
        FROM pg_stat_activity
        WHERE state = 'active' OR state = 'idle in transaction';
    """)
    rows = cur.fetchall()
    for row in rows:
        print(row)
    conn.close()
except Exception as e:
    print(e)
