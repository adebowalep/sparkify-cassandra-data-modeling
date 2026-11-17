# Sparkify: Data Modeling with Apache Cassandra

Query-driven data modeling and a Python ETL pipeline for Sparkify's music streaming events, built on Apache Cassandra.

## Business problem
Sparkify's analytics team wants to know what users listen to, but the activity data sits in a directory of daily CSV files. This project consolidates those files and models Cassandra tables that answer three specific questions.

## Queries supported
1. Artist, song title and song length for `sessionId = 338` and `itemInSession = 4`.
2. Artist, song (sorted by `itemInSession`) and user first/last name for `userId = 10` and `sessionId = 182`.
3. Every user (first and last name) who listened to `All Hands Against His Own`.

(Data model, results and run instructions are added in later commits.)
