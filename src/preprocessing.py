"""Part I of the pipeline: consolidate the daily event files into one CSV.

Kept as a small module so the notebook and the tests run exactly the same code.
"""
import csv
from pathlib import Path

OUTPUT_COLUMNS = ['artist', 'firstName', 'gender', 'itemInSession', 'lastName', 'length',
                  'level', 'location', 'sessionId', 'song', 'userId']


def list_event_files(raw_dir):
    """Top-level *.csv files in raw_dir, in sorted (date) order. Sub-directories are ignored."""
    return sorted(Path(raw_dir).glob('*.csv'))


def read_playback_rows(paths):
    """Yield one dict per playback event (non-empty artist) from the raw event files."""
    for path in paths:
        with open(path, 'r', encoding='utf8', newline='') as csvfile:
            for record in csv.DictReader(csvfile):
                if record['artist'] != '':
                    yield record


def write_processed_file(paths, output_file):
    """Write the playback events to output_file and return the number of records written.

    The file is opened in write mode, so running this again regenerates it
    rather than appending duplicates.
    """
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with open(output_file, 'w', encoding='utf8', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(OUTPUT_COLUMNS)
        for record in read_playback_rows(paths):
            writer.writerow([record[col] for col in OUTPUT_COLUMNS])
            count += 1
    return count
