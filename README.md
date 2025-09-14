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
    docker-compose exec kafka /bin/bash -c \
    'cat data-files/jobs.kafka | kafka-console-producer.sh \
    --bootstrap-server localhost:9092 \
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
