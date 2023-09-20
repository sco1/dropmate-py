from collections import abc
from pathlib import Path

from dropmate_py.parser import ColumnIndices, FauxSeries

CONSOLIDATED_HEADERS = (
    "uid",
    "flight_index",
    "start_time_utc",
    "end_time_utc",
    "start_barometric_altitude_msl_ft",
    "end_barometric_altitude_msl_ft",
)


def _keyer(short_record: str) -> tuple[str, int]:  # pragma: no cover
    """
    Sorting key based on consolidated drop record.

    NOTE: It is assumed that the first column is the Dropmate UID and second column is the flight
    index.
    """
    split_record = short_record.split(",")
    return (split_record[0], int(split_record[1]))


def consolidate_drop_records(
    log_dir: Path,
    log_pattern: str,
    out_filepath: Path,
    keep_headers: abc.Sequence[str] = CONSOLIDATED_HEADERS,
    write_file: bool = True,
) -> list[str]:
    """
    Merge a directory of Dropmate drop record outputs into a deduplicated, simplified drop record.

    To support legacy Dropmate app data formats, a subset of headers are selected that should be
    common across all versions:
        * `uid`
        * `flight_index`
        * `start_time_utc`
        * `end_time_utc`
        * `start_barometric_altitude_msl_ft`
        * `end_barometric_altitude_msl_ft`

    It is assumed that these headers are present, no checking is done on the input log files.
    """
    seen_logs = set()
    consolidated_records = []
    for log in log_dir.glob(log_pattern):
        log_lines = log.read_text().splitlines()
        indices = ColumnIndices.from_header(log_lines[0])

        for drop_record in log_lines[1:]:
            record_series = FauxSeries(drop_record.split(","), indices)
            drop_key = (record_series["uid"], record_series["flight_index"])

            if drop_key not in seen_logs:
                shortened = ",".join(record_series[col] for col in keep_headers)
                consolidated_records.append(shortened)
                seen_logs.add(drop_key)

    consolidated_records.sort(key=_keyer)

    if write_file:
        with out_filepath.open("w") as f:
            f.write(f"{','.join(keep_headers)}\n")
            f.writelines(f"{record}\n" for record in consolidated_records)

    return consolidated_records
