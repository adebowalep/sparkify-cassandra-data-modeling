# Verification Report

This report separates four kinds of evidence, because they are not equally strong.

| Kind | Meaning |
|---|---|
| **Recorded** | Observed in an earlier execution of this project. Not re-run for this report. |
| **Re-run** | Executed again while restructuring the repository (November 17, 2026). |
| **Not reproduced** | Could not be run in the current environment. |
| **Inferred** | Follows from the code or table design but was not directly measured. |

## Recorded execution (earlier version of the notebook)
The first complete version of the notebook was executed top to bottom against a local Apache Cassandra 4.1 (Docker container, single node) with `cassandra-driver` 3.30.1 and Python 3.12, with no exceptions. The same notebook was later run in the Udacity course workspace (older driver), where it also completed. That version is in Git history (commit `7a5f44c`, notebook at its original path).

| Check | Recorded result |
|---|---|
| Event files read | 30 (2018-11-01 to 2018-11-30) |
| Playback records written | 6,820, 11 columns in the required order |
| Query 1 (session 338, item 4) | Faithless, Music Matters (Mark Knight Dub), 495.3073 |
| Query 2 (user 10, session 182) | 4 rows (items 0 to 3), one user, in item order |
| Query 3 ("All Hands Against His Own") | 3 listeners: Jacqueline Lynch, Tegan Levine, Sara Johnson |
| No `ALLOW FILTERING` | none of the queries uses it |

**Key-count validation (recorded):**

| Table | Distinct source keys | Cassandra rows |
|---|---:|---:|
| `song_by_session_item` | 6,820 | 6,820 |
| `song_by_user_session` | 6,820 | 6,820 |
| `listeners_by_song` | 6,618 | 6,618 |

The third table has fewer rows by design: it stores one row per distinct (song, listener) pair, and 155 pairs were played more than once.

**Idempotence (recorded):** regenerating the CSV produced a byte-identical file, and loading each table twice without dropping it left the row counts unchanged (6,820 / 6,820 / 6,618), because loads upsert on the primary key.

## Re-run during restructuring

| Check | Result |
|---|---|
| `pytest` (11 tests, no Cassandra needed) | 11 passed |
| Regenerated `data/processed/event_datafile_new.csv` vs. the committed file | byte-identical (also asserted by a test) |
| Primary-key uniqueness on the real data (pandas) | 6,820 distinct `(session, item)`; 6,820 distinct `(user, session, item)`; 6,618 distinct `(song, user)` |
| Part I of the notebook, run from `notebooks/` | 30 files found, 6,820 records written, 11 columns, assertions pass |
| Notebook code cells | all 18 compile |
| Source-data facts used in the docs | 776 sessions, 96 users, no session shared by two users, largest session 117 plays, most distinct listeners for one song 22 |

## Not reproduced
- **The restructured notebook was not executed against Cassandra** in this pass. Docker Desktop's engine did not start in the environment used for the restructuring (the daemon socket refused connections), and Cassandra is not installed natively. The notebook therefore has **no saved outputs** right now.
- This means the new cells added during restructuring have not yet run against a database: the connection retry, the `RESET_TABLES` switch, and the **cross-check cell** that asserts each Cassandra answer (including the Query 2 order) against a pandas recomputation. The query and table definitions themselves are unchanged from the recorded version.

To reproduce, start Cassandra (`docker compose up -d`), run the notebook top to bottom, and the cross-check and key-count cells will assert the results above.

## Inferred (not measured)
- Ordered results for Query 2 follow from `CLUSTERING ORDER BY (item_in_session ASC)`; the recorded output showed items 0 to 3 in order.
- Behaviour at larger scale (partition growth, hotspots, multi-node consistency) is discussed in `data-model.md` as design reasoning, not as measurements.

## What this does not show
A successful run on a single local node with about 7,000 rows shows that the model answers the three queries correctly. It is not evidence of production readiness, performance or availability.
