"""一次性迁移：rules.layer CHECK 约束加 EVENT_TOPIC（同步 docs/v36/11_DATABASE_SCHEMA.sql 修改）"""
import psycopg2

conn = psycopg2.connect(host="127.0.0.1", port=5432, dbname="otcg",
                        user="postgres", password="postgres", connect_timeout=5)
conn.autocommit = True
cur = conn.cursor()

cur.execute("""
    SELECT conname, pg_get_constraintdef(oid)
    FROM pg_constraint
    WHERE conrelid = 'rules'::regclass AND contype = 'c'
""")
rows = cur.fetchall()
print(f"CHECK constraints on rules: {len(rows)}")

target = None
for name, definition in rows:
    print(f"  {name}: {definition}")
    if "layer" in definition and "EVENT_TOPIC" not in definition:
        target = (name, definition)

if target is None:
    already = [d for _, d in rows if "layer" in d and "EVENT_TOPIC" in d]
    if already:
        print("ALREADY MIGRATED — nothing to do")
    else:
        print("NO layer CHECK found on rules — abort")
else:
    name, _def = target
    new_def = ("CHECK ((layer)::text = ANY "
               "(ARRAY['BASELINE'::text, 'CYCLE_CONTEXT'::text, "
               "'DAILY_ACTIVATION'::text, 'EVENT_TOPIC'::text]))")
    cur.execute(f"ALTER TABLE rules DROP CONSTRAINT {name}")
    cur.execute(f"ALTER TABLE rules ADD CONSTRAINT {name} {new_def}")
    # 验证
    cur.execute("SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname = %s", (name,))
    print(f"\n✓ Migrated. New def: {cur.fetchone()[0]}")

# 验证 EVENT_TOPIC 插入可行
cur.execute("SELECT count(*) FROM rules WHERE layer = 'EVENT_TOPIC'")
print(f"Existing EVENT_TOPIC rows in DB: {cur.fetchone()[0]}")
conn.close()
print("\nDONE")
