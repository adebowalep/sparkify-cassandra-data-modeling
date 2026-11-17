# Sparkify Music Analytics — Cassandra Data Modeling

## Short description
A learning project that turns 30 daily music-streaming activity files into three query-specific Apache Cassandra tables. A small Python ETL consolidates the data, and each table is designed around one analytical question. The query results are cross-checked against the source data.

## Technologies
Python, Apache Cassandra 4.1, CQL, the Cassandra Python driver, pandas, pytest, Jupyter Notebook, Docker Compose (local Cassandra).

## What I did
- Wrote a repeatable Python ETL that discovers the daily files, drops non-playback events and writes an 11-column consolidated CSV (6,820 records).
- Designed one Cassandra table per query, choosing partition and clustering keys from the `WHERE` clause of each question.
- Loaded the tables with prepared statements and strict conversion of required fields.
- Validated the model two ways: row counts against distinct primary keys in the source, and query answers against results computed independently with pandas (including the ordering of Query 2).
- Added unit tests for the preprocessing, a Docker Compose file for a local Cassandra, and documentation of the design trade-offs.

## Main technical challenge
In Cassandra the primary key decides both where data lives and which queries are possible, so the model has to start from the questions rather than from the entities. The challenge was choosing keys that match each query exactly (no `ALLOW FILTERING`) while keeping each row unique. For example, `(song, user_id)` makes each listener a separate row, whereas `song` alone would overwrite listeners.

## Engineering highlights
- ETL preprocessing with deterministic file order, header-based column selection and idempotent output.
- Query-driven table design with a composite partition key and `CLUSTERING ORDER BY` for server-side ordering.
- Deliberate denormalization, with its costs documented.
- Distinct-listener semantics: 6,820 plays but 6,618 distinct song and user pairs.
- Independent validation of results rather than trusting the database to confirm itself.

## Results (sample data)
- Query 1 returned Faithless, "Music Matters (Mark Knight Dub)", 495.3073 seconds.
- Query 2 returned four plays for one user in item order.
- Query 3 returned three distinct listeners.
- Table row counts matched the distinct primary-key counts: 6,820 / 6,820 / 6,618.

## Limitations
Single local node, replication factor 1, about 7,000 rows. This demonstrates modeling technique, not production performance, availability or scale. The dataset is a course-provided sample, and Sparkify is a fictional scenario.

## Recommended visuals
`docs/images/architecture.svg` (ETL and table design). Optionally a screenshot of the notebook's query-result cells and the cross-check cell.
