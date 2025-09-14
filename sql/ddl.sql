
-- Create Users table
-- Users tablosunu yeniden oluştur (varsa silip tekrar açıyoruz)
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    userid   BIGINT PRIMARY KEY,
    location TEXT NOT NULL
);
-- Create Jobs table
DROP TABLE IF EXISTS jobs;

CREATE TABLE jobs (
    jobidentifier BIGINT PRIMARY KEY,
    userid        BIGINT REFERENCES users(userid),
    jobcreatedate TIMESTAMPTZ,
    jobdate       TIMESTAMPTZ,
    jobstatus     TEXT,
    location      TEXT,
    revenue       NUMERIC,
    servicename   TEXT
);
--- Create Indexes for optimization
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_jobs_userid   ON jobs(userid);