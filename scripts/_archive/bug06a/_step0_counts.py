"""Step 0: DB baseline count check."""
import psycopg2

conn = psycopg2.connect("postgres://postgres:postgres@127.0.0.1:5432/otcg")
cur = conn.cursor()

for t in ["rules", "evidence", "mappings"]:
    cur.execute(f"SELECT count(*) FROM {t}")
    print(f"{t}: {cur.fetchone()[0]}")

cur.execute("SELECT status, count(*) FROM rules GROUP BY status ORDER BY status")
for row in cur.fetchall():
    print(f"rules status={row[0]}: {row[1]}")

conn.close()
