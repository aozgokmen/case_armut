<img width="180" alt="armut_logo" src="https://github.com/user-attachments/assets/94106cdb-7c90-4609-aea2-e4bd2fbe4c35" />

# Armut Case – ETL Pipeline with Kafka & Postgres

This project was developed as part of a **technical case study for Armut**.  
It demonstrates a simple yet effective **ETL pipeline** where **user** and **job** data are ingested through **Kafka** and stored in **Postgres** for analytical queries.  
The entire environment is orchestrated with **Docker Compose**, ensuring a fully reproducible and easy-to-run setup.

---

## ⚙️ Setup & 🚀 Usage

Follow these steps to run the project locally:

1. **Clone the repository**
   ```bash
   git clone https://github.com/aozgokmen/case_armut.git
   cd case_armut
   ```
2. **Start fresh environment**
   ```bash
   docker compose down -v   # remove containers, networks, and volumes
   docker compose up -d     # start everything in background
    ```
3. **Reset DB tables**
   ```bash
   docker compose exec postgres psql -U postgres -d armut -c "TRUNCATE jobs, users;"
   ```
4. **Load initial users into Postgres**
    ```bash
    docker compose run --rm users-loader
    docker compose exec postgres psql -U postgres -d armut -c "SELECT COUNT(*) FROM users;"
    ```

6. **Check Kafka Topics**
   ```bash
   docker compose exec kafka kafka-topics.sh --list --bootstrap-server kafka:9092
   ```
7. **Send job events from file into Kafka "jobs" topic (If the topic doesn't exist, Kafka may auto-create it)**
   ```bash
    docker compose exec kafka /bin/bash -c \
    'cat data-files/jobs.kafka | kafka-console-producer.sh \
    --bootstrap-server kafka:9092 \
    --property parse.key=true \
    --property key.separator="|" \
    --topic jobs'
    ```
8. **Check Kafka Topics**
   ```bash
   docker compose up -d jobs-consumer
   # or run interactively
   docker compose run --rm jobs-consumer
   ```
8. **Verify Data in Postgres**
   ```bash
    docker compose exec postgres \
    psql -U postgres -d armut \
    -c "SELECT jobidentifier, userid, jobcreatedate, jobdate, jobstatus, location, revenue, servicename FROM jobs ORDER BY jobidentifier DESC LIMIT 5;"
   ```
## 📊 Final Case Query

After loading **users** and sending **jobs** into Kafka, you can verify the pipeline with the following query in Postgres:

   ```bash
   docker compose exec -T postgres psql -U postgres -d armut -c "
   SELECT j.userid
   FROM jobs j
   JOIN users u ON j.userid = u.userid
   WHERE j.location = 'LOC_1294'
   AND u.location <> j.location
   GROUP BY j.userid
   HAVING SUM(j.revenue) > 0
   ORDER BY SUM(j.revenue) DESC
   LIMIT 5;
   "
   ```

## 📊 Example Parametrized Queries

## Jobs by Location
 ```bash
PREPARE jobs_by_location(text) AS
SELECT jobidentifier, userid, jobstatus, revenue, jobdate
FROM jobs
WHERE location = $1
ORDER BY jobdate DESC
LIMIT 5;
 ```
 ```bash
EXECUTE jobs_by_location('LOC_1294');
 ```

## Jobs by Service Name
 ```bash
PREPARE jobs_by_service(text) AS
SELECT jobidentifier, userid, jobstatus, revenue, jobdate
FROM jobs
WHERE servicename = $1
ORDER BY jobdate DESC
LIMIT 5;
 ```
 ```bash
EXECUTE jobs_by_service('SERVICE_42');
 ```

## Questions 

The jobs data given to you was static even though it was in a Kafka topic. Would you do anything differently if new jobs arrived continuously to the Kafka topic? If so, what would you do?


- If job messages in Kafka weren’t static but streaming continuously, I’d set up the consumer as a permanent service instead of a one-off script; so data is processed in real time as it arrives. I’d use event time and watermarks to handle late or out-of-order events, and make sure offset management / checkpointing is in place so failures don’t cause data loss or duplicate processing. I’d scale Kafka by adding partitions and running multiple consumers; use larger batches, compression, and efficient serialization (like Avro or Protobuf) to cut down message size and overhead. I’d perform transformations closer to the source (in the streaming layer) to catch issues early and reduce downstream load. Finally, I’d add monitoring (latency, consumer lag, error rates, throughput) so I can see bottlenecks early.

⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

Would you do anything differently if the amount of kafka records in Jobs topic and the user file
increased significantly

- If the number of Kafka records in the Jobs topic and the size of the user file increased significantly, I would adjust several parts: increase producer batch size and set linger.ms so messages are sent in groups rather than one-by-one; use compression to reduce message size and network usage. For large messages, I might store the heavy payload elsewhere and keep only references in Kafka. Also, I’d enforce retention policies in Kafka so old unneeded messages don’t pile up (by time or size). On the consumer side, I’d increase fetch.min.bytes, fetch.max.wait.ms, max.partition.fetch.bytes etc., and possibly run more consumer instances in parallel. Lastly, I’d set up monitoring (lag, throughput, latency, resource usage) so I can detect performance issues early.

⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

Would your approach be any different if you had to use 10-20 datasets? Would you change where you do the data transformations?


- Yes, I would adjust where and how transformations happen when many datasets are involved. Instead of doing all transformations in the consumer script or right after ingestion, I’d set up a dedicated transformation layer likely inside a data warehouse or using something like dbt  that centralizes schema normalization, cleaning, and enrichment. I’d use staging tables/raw layers to store incoming data as is, then perform transformations (e.g. type casting, field standardization, missing value handling) in batch or scheduled jobs within the warehouse. For very large or frequent datasets, more transformation at the source (e.g. in Kafka stream processing, or micro-services upstream) might help reduce load downstream. In short: with many datasets, it’s better to push “where possible” transformation logic into the DW or a transformation layer rather than doing everything in small scripts; this improves maintainability, scalability, and makes it easier to monitor data quality.


