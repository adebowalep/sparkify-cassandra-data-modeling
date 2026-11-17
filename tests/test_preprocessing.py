"""Tests for the Part I preprocessing. None of them need a running Cassandra server."""
import csv
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from preprocessing import (OUTPUT_COLUMNS, list_event_files,  # noqa: E402
                           read_playback_rows, write_processed_file)

RAW_DIR = ROOT / 'data' / 'raw'
RAW_HEADER = ['artist', 'auth', 'firstName', 'gender', 'itemInSession', 'lastName', 'length',
              'level', 'location', 'method', 'page', 'registration', 'sessionId', 'song',
              'status', 'ts', 'userId']


def raw_row(artist='', song='', first='Ann', last='Lee', item=0, session=1, user=1, length='200.5'):
    row = dict.fromkeys(RAW_HEADER, '')
    row.update(artist=artist, song=song, firstName=first, lastName=last, itemInSession=item,
               sessionId=session, userId=user, length=length, gender='F', level='free',
               location='Somewhere, XX')
    return row


def write_raw(path, rows):
    with open(path, 'w', encoding='utf8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=RAW_HEADER)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def processed(tmp_path):
    """The real dataset, processed into a temporary file."""
    out = tmp_path / 'event_datafile_new.csv'
    count = write_processed_file(list_event_files(RAW_DIR), out)
    return out, count


# 1. file discovery
def test_all_daily_files_discovered_in_order():
    files = list_event_files(RAW_DIR)
    assert len(files) == 30
    assert [f.name for f in files] == [f'2018-11-{d:02d}-events.csv' for d in range(1, 31)]


def test_discovery_ignores_subdirectories_and_non_csv(tmp_path):
    write_raw(tmp_path / '2018-11-01-events.csv', [])
    (tmp_path / '.ipynb_checkpoints').mkdir()
    write_raw(tmp_path / '.ipynb_checkpoints' / '2018-11-01-events-checkpoint.csv', [])
    (tmp_path / 'notes.txt').write_text('not data')
    assert [f.name for f in list_event_files(tmp_path)] == ['2018-11-01-events.csv']


# 2. output schema
def test_output_schema_and_field_counts(processed):
    out, count = processed
    with open(out, encoding='utf8', newline='') as f:
        rows = list(csv.reader(f))
    assert rows[0] == OUTPUT_COLUMNS
    assert len(OUTPUT_COLUMNS) == 11
    assert all(len(r) == 11 for r in rows)
    assert len(rows) - 1 == count


# 3. playback filtering
def test_non_playback_events_are_excluded(tmp_path):
    raw = tmp_path / 'raw'
    raw.mkdir()
    write_raw(raw / 'a.csv', [raw_row(artist='A', song='S1'), raw_row(artist='', song=''),
                              raw_row(artist='B', song='S2')])
    out = tmp_path / 'out.csv'
    assert write_processed_file(list_event_files(raw), out) == 2
    assert [r['artist'] for r in csv.DictReader(open(out, encoding='utf8'))] == ['A', 'B']


def test_real_data_counts(processed):
    _, count = processed
    raw_total = sum(len(pd.read_csv(f)) for f in list_event_files(RAW_DIR))
    assert count == 6820
    assert count < raw_total  # the rest are non-playback events


# 4. repeatable preprocessing
def test_running_twice_does_not_duplicate_rows(tmp_path):
    out = tmp_path / 'out.csv'
    files = list_event_files(RAW_DIR)
    first = write_processed_file(files, out)
    content_after_first = out.read_bytes()
    second = write_processed_file(files, out)
    assert first == second
    assert out.read_bytes() == content_after_first


def test_committed_processed_file_matches_regenerated(processed):
    out, _ = processed
    committed = ROOT / 'data' / 'processed' / 'event_datafile_new.csv'
    assert committed.read_bytes() == out.read_bytes()


# 5. primary-key uniqueness on the real data
def test_primary_key_uniqueness_on_real_data(processed):
    out, count = processed
    df = pd.read_csv(out)
    assert len(df[['sessionId', 'itemInSession']].drop_duplicates()) == count == 6820
    assert len(df[['userId', 'sessionId', 'itemInSession']].drop_duplicates()) == count
    # listeners_by_song stores distinct (song, user) pairs: repeat plays collapse
    assert len(df[['song', 'userId']].drop_duplicates()) == 6618 < count


# 6. edge cases with small fixtures
def test_field_mapping_and_quoting(tmp_path):
    raw = tmp_path / 'raw'
    raw.mkdir()
    write_raw(raw / 'a.csv', [raw_row(artist='Doe, John', song='He said "hi"', first='Zoe', last='Q',
                                      item=7, session=42, user=9, length='12.5')])
    out = tmp_path / 'out.csv'
    write_processed_file(list_event_files(raw), out)
    row = next(csv.DictReader(open(out, encoding='utf8', newline='')))
    assert row['artist'] == 'Doe, John' and row['song'] == 'He said "hi"'
    assert (row['firstName'], row['lastName'], row['itemInSession']) == ('Zoe', 'Q', '7')
    assert (row['sessionId'], row['userId'], row['length']) == ('42', '9', '12.5')


def test_repeated_song_listener_pairs_collapse_to_one_listener(tmp_path):
    raw = tmp_path / 'raw'
    raw.mkdir()
    write_raw(raw / 'a.csv', [raw_row(artist='A', song='Hit', user=1, session=1, item=0),
                              raw_row(artist='A', song='Hit', user=1, session=2, item=3),
                              raw_row(artist='A', song='Hit', user=2, session=3, item=1)])
    out = tmp_path / 'out.csv'
    count = write_processed_file(list_event_files(raw), out)
    df = pd.read_csv(out)
    assert count == 3
    assert len(df[['sessionId', 'itemInSession']].drop_duplicates()) == 3  # every play is a distinct row
    assert len(df[['song', 'userId']].drop_duplicates()) == 2              # but only two distinct listeners


def test_read_playback_rows_is_lazy_and_ordered(tmp_path):
    write_raw(tmp_path / 'b.csv', [raw_row(artist='B', song='x')])
    write_raw(tmp_path / 'a.csv', [raw_row(artist='A', song='y')])
    rows = list(read_playback_rows(list_event_files(tmp_path)))
    assert [r['artist'] for r in rows] == ['A', 'B']
