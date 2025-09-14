# Case Armut ETL Project

This project implements a simple **ETL pipeline** that ingests user and job data via **Kafka** and stores it into **Postgres** for analytical queries.  
The whole setup is orchestrated with **Docker Compose**.

---

## ⚙️ Setup

Follow these steps to run the project locally:

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/case_armut.git
   cd case_armut
   ```

2. **Build and start services**
   ```bash
   docker compose up -d --build
   ```

3. **Load initial users into Postgres**
   ```bash
   docker compose run --rm users-loader
   ```

4. **Send job events to Kafka**
   ```bash
   docker compose exec -T kafka kafka-console-producer.sh      --broker-list kafka:9092      --topic jobs < ./data-files/jobs.kafka
   ```

5. **Check results in Postgres**
   ```bash
   docker compose exec postgres      psql -U postgres -d armut -c "SELECT * FROM jobs LIMIT 10;"
   ```

---

## 📊 Example Query

```sql
SELECT jobstatus, COUNT(*) AS total_jobs, SUM(revenue) AS total_revenue
FROM jobs
GROUP BY jobstatus
ORDER BY total_jobs DESC;
```

---

## 🛠 Stack
- **Postgres** – Database
- **Kafka** – Messaging
- **Docker Compose** – Orchestration
- **Python** – ETL scripts

---

## 📂 Structure
```
case_armut/
├── data-files/        # Input data (users.csv, jobs.kafka)
├── load_users.py      # Load users into Postgres
├── load_consumer.py   # Kafka consumer for jobs
├── docker-compose.yml # Service definitions
└── README.md
```

---

✅ After completing the setup, you will have a running ETL pipeline that consumes Kafka job events and persists them into Postgres for analysis.
