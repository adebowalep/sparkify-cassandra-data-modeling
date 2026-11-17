# Rubric validation: Sparkify Data Modeling with Apache Cassandra

**Execution environment:** Cassandra 4.1 (Docker container, 127.0.0.1:9042), cassandra-driver 3.30.1, Python 3.12.
The notebook `Sparkify_Cassandra_Project.ipynb` was executed top to bottom with `jupyter nbconvert --execute`, with no exceptions. Outputs are saved in the notebook.
The original `Project_1B_ Project_Template.ipynb` and `event_data/` files were not modified.

| Rubric item | Status | Evidence |
|---|---|---|
| ETL: `event_datafile_new.csv` genuinely generated | PASS | Part I: 30 files read, 6,820 playback records, 11 columns in the required order; assertions on file existence, header and field counts. File included in `submission/`. |
| ETL: correct datatypes in CREATE statements | PASS | `int` for ids and item number, `double` for length, `text` for names/artist/song. |
| Correct table per query | PASS | `song_by_session_item`, `song_by_user_session`, `listeners_by_song`. |
| SELECTs return exact answers without ALLOW FILTERING | PASS | Q1: Faithless / Music Matters (Mark Knight Dub) / 495.3073. Q2: 4 rows for Sylvie Cruz, in itemInSession order 0-3. Q3: Jacqueline Lynch, Tegan Levine, Sara Johnson. "ALLOW FILTERING" appears only in explanatory text, not in any query. |
| Meaningful lowercase table names | PASS | See table names above. |
| Column order reflects partitioning and clustering | PASS | Keys are listed first in each table: `(session_id, item_in_session)`, `((user_id, session_id), item_in_session)`, `(song, user_id)`. |
| Primary key uniquely identifies rows | PASS | Checked against the data: no duplicate keys for Q1 and Q2 (6,820 distinct). Q3 has 6,618 distinct (song, user) pairs: repeat plays collapse into one listener by design. The "Data checks" cell compares Cassandra row counts with distinct keys in the CSV: all match. |
| Query 2 ordering through clustering | PASS | `CLUSTERING ORDER BY (item_in_session ASC)`; no ORDER BY and no Python sort. |
| Presentation: description and key rationale per query | PASS | Markdown cell before each table (question, partition and clustering keys, grain). |
| Presentation: clean, modular code | PASS | Helper functions (`read_playback_rows`, `load_table`, `required_*`); TODO placeholders and instruction comments removed; results shown as pandas DataFrames from the real SELECTs. |
| Re-run does not duplicate records | PASS | The CSV is rewritten (hash identical on rerun). Loading each table twice without dropping left the row counts unchanged (6820 / 6820 / 6618). |
| Prepared statements | PASS | All inserts use `session.prepare`; empty required values raise an error instead of being loaded. |
| Cleanup and shutdown | PASS | Drop cell is optional (`DROP_TABLES = False` by default, so tables remain for screenshots). It drops only the three project tables. Session and cluster are shut down in the last cell. |

## Not covered
- Executed here on Python 3.12 with driver 3.30. The Udacity workspace has an older driver (no `ResultSet.one()`); the count check was changed to `list(...)[0][0]`, which works on both. If the grader requires drop commands to have run, set `DROP_TABLES = True` before the final run.
- `COUNT(*)` is used once in the data-check cell as a verification scan, never in the answer queries.
