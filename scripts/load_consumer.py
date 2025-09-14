import os
import json
import time
import psycopg2
from confluent_kafka import Consumer
from dateutil import parser

# ENV
PG_DSN = os.environ["PG_DSN"]
KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092")
KAFKA_GROUP = os.environ.get("KAFKA_GROUP", "etl-jobs-consumer")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "jobs")

def parse_timestamp(value):
    if not value:
        return None
    try:
        return parser.parse(value).strftime("%Y-%m-%d %H:%M:%S%z")
    except Exception as e:
        print(f"⚠️ Timestamp parse error: {value} ({e})")
        return None

def main():
    # Kafka connect
    for i in range(10):
        try:
            consumer = Consumer({
                "bootstrap.servers": KAFKA_BOOTSTRAP,
                "group.id": KAFKA_GROUP,
                "auto.offset.reset": "earliest"
            })
            consumer.subscribe([KAFKA_TOPIC])
            print("✅ Kafka connected & subscribed")
            break
        except Exception as e:
            print(f"⏳ Waiting Kafka... {i+1}/10 ({e})")
            time.sleep(3)
    else:
        raise Exception("❌ Kafka connection failed")

    # Postgres connect
    for i in range(10):
        try:
            conn = psycopg2.connect(PG_DSN)
            cur = conn.cursor()
            print("✅ Postgres connected")
            break
        except Exception as e:
            print(f"⏳ Waiting Postgres... {i+1}/10 ({e})")
            time.sleep(3)
    else:
        raise Exception("❌ Postgres connection failed")

    UPSERT_SQL = """
    INSERT INTO jobs(jobidentifier, userid, jobcreatedate, jobdate, jobstatus, location, revenue, servicename)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (jobidentifier) DO UPDATE SET
      userid=EXCLUDED.userid,
      jobcreatedate=EXCLUDED.jobcreatedate,
      jobdate=EXCLUDED.jobdate,
      jobstatus=EXCLUDED.jobstatus,
      location=EXCLUDED.location,
      revenue=EXCLUDED.revenue,
      servicename=EXCLUDED.servicename;
    """

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print("⚠️ Kafka error:", msg.error())
                continue

            payload = msg.value().decode("utf-8").strip()
            print(f"📥 Raw msg: {payload}")

            # Format: jobid|{JSON}
            if "|" in payload:
                jobid_str, json_str = payload.split("|", 1)
                jobidentifier = int(jobid_str)
                rec = json.loads(json_str)
            else:
                rec = json.loads(payload)
                jobidentifier = int(rec["JOBIDENTIFIER"])

            userid        = int(rec.get("USERID"))
            jobcreatedate = parse_timestamp(rec.get("JOBCREATEDATE"))
            jobdate       = parse_timestamp(rec.get("JOBDATE"))
            jobstatus     = rec.get("JOBSTATUS")
            location      = rec.get("LOCATION")
            revenue       = float(rec.get("REVENUE", 0))
            servicename   = rec.get("SERVICENAME")

            # ensure user
            cur.execute("INSERT INTO users(userid, location) VALUES (%s,%s) ON CONFLICT (userid) DO NOTHING;", (userid, location))
            # upsert job
            cur.execute(UPSERT_SQL, (jobidentifier, userid, jobcreatedate, jobdate, jobstatus, location, revenue, servicename))
            conn.commit()

            print(f"💾 Job saved: {jobidentifier} | User={userid} | Created={jobcreatedate} | Date={jobdate}")

    except KeyboardInterrupt:
        print("🛑 Stopped by user")
    finally:
        conn.close()
        consumer.close()
        print("✅ Connections closed")

if __name__ == "__main__":
    main()