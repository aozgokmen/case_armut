import json
import os
import psycopg2

# PostgreSQL bağlantısı
PG_DSN = os.environ.get("PG_DSN", "postgresql://postgres:postgres@postgres:5432/armut")
conn = psycopg2.connect(PG_DSN)
cur = conn.cursor()

with open("/data/users.ndjson", "r", encoding="utf-8") as f:
    batch = []
    BATCH_SIZE = 1000  # her seferde 1000 kayıt insert

    for line in f:
        if not line.strip():
            continue  # boş satır varsa atla
        rec = json.loads(line)
        user_id = rec["USERID"]
        location = rec["LOCATION"]
        batch.append((user_id, location))

        if len(batch) >= BATCH_SIZE:
            cur.executemany(
                """
                INSERT INTO users(USERID, LOCATION)
                VALUES (%s, %s)
                ON CONFLICT (userid)
                DO UPDATE SET LOCATION = EXCLUDED.LOCATION
                """,
                batch
            )
            conn.commit()
            print(f"✅ {len(batch)} kayıt yüklendi")
            batch.clear()

    # kalan batch'i yükle
    if batch:
        cur.executemany(
            """
            INSERT INTO users(USERID, LOCATION)
            VALUES (%s, %s)
            ON CONFLICT (USERID)
            DO UPDATE SET LOCATION = EXCLUDED.LOCATION
            """,
            batch
        )
        conn.commit()
        print(f"✅ {len(batch)} kayıt yüklendi (final batch)")

cur.close()
conn.close()
print("🎉 Users yükleme tamamlandı!")