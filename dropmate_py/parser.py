from __future__ import annotations

import datetime as dt
import itertools
import operator
import typing as t
from collections import abc
from dataclasses import dataclass, fields
from enum import Enum
from pathlib import Path


@dataclass
class ColumnIndices:
    """
    Column index in the parsed Dropmate compiled log CSV.

    Attribute names are assumed to correspond to the Dropmate log header name. Columns contained may
    vary by Dropmate app version, so if they are not present in the compiled log they will remain at
    a value of `-1`, indicating they were not found.

    Current header names are assumed to be as of Dropmate app version 1.5.16, and should be unified
    across the iOS and Android app outputs (this isn't the case for older app versions).
    """

    serial_number: int = -1
    uid: int = -1
    battery: int = -1
    device_health: int = -1
    firmware_version: int = -1
    log_timestamp: int = -1
    log_altitude: int = -1
    total_flights: int = -1
    flights_over_18kft: int = -1
    recorded_flights: int = -1
    flight_index: int = -1
    start_time_utc: int = -1
    end_time_utc: int = -1
    start_barometric_altitude_msl_ft: int = -1
    end_barometric_altitude_msl_ft: int = -1
    dropmate_internal_time_utc: int = -1
    last_scanned_time_utc: int = -1
    scan_device_type: int = -1
    scan_device_os: int = -1
    dropmate_app_version: int = -1

    def __iter__(self) -> t.Generator[str, None, None]:
        for f in fields(self):
            yield f.name

    @classmethod
    def from_header(cls, header: str) -> ColumnIndices:
        """Attempt to match attribute names to their corresponding data columns."""
        indices = ColumnIndices()

        # Some column names may have stray spaces in them, listify so we can iterate over repeatedly
        col_names = [c.strip().lower() for c in header.split(",")]
        for query_col in indices:
            for idx, col in enumerate(col_names):
                if col == query_col:
                    setattr(indices, query_col, idx)

        return indices

    def __str__(self) -> str:  # pragma: no cover
        return ", ".join(f"({f}, {getattr(self, f)})" for f in self)


class Health(str, Enum):  # noqa: D101
    GOOD = "good"
    POOR = "poor"


@dataclass
class FauxSeries:
    """
    Helper container to support column access by name of a raw log line.

    NOTE: `raw_columns` is assumed to already be split.
    """

    raw_columns: abc.Sequence[str]
    indices: ColumnIndices

    def __getitem__(self, key: str) -> str:
        idx = getattr(self.indices, key, None)
        if idx is None or idx == -1:
            raise KeyError(f"Column {key} not present in log file.")

        val = self.raw_columns[idx]
        if not isinstance(val, str):  # pragma: no cover
            # Shouldn't ever get here but add the guard just in case
            raise ValueError("Provided log data contains non-string value(s).")

        return val


T = t.TypeVar("T")


def _try_conv(in_val: str, converter: abc.Callable[[str], T]) -> T | None:
    """Attempt the specified conversion if `in_val` is not `"na"`, otherwise return `None`."""
    if in_val == "na":
        return None

    return converter(in_val)


@dataclass
class DropRecord:
    """
    Represent a Dropmate drop record.

    Drop records compare equal using both the Dropmate UID and the record's flight index, as
    determined by the Dropmate hardware.

    NOTE: A Dropmate with no drops currently scan with the following columns set to `"na"`, and will
    be set to `None`:
        * `flight_index`
        * `start_time_utc`
        * `end_time_utc`
        * `start_barometric_altitude_msl_ft`
        * `end_barometric_altitude_msl_ft`
    """

    serial_number: str
    uid: str
    battery: Health
    device_health: Health
    firmware_version: float
    flight_index: int | None
    start_time_utc: dt.datetime | None
    end_time_utc: dt.datetime | None
    start_barometric_altitude_msl_ft: int | None
    end_barometric_altitude_msl_ft: int | None
    dropmate_internal_time_utc: dt.datetime
    last_scanned_time_utc: dt.datetime

    def __eq__(self, other: t.Any) -> bool:
        if not isinstance(other, DropRecord):
            raise NotImplementedError(
                f"Can only compare between {type(self).__name__}, received: {type(other).__name__}"
            )

        return (self.uid, self.flight_index) == (other.uid, other.flight_index)

    def __hash__(self) -> int:
        return hash((self.uid, self.flight_index))

    @classmethod
    def from_raw(cls, log_line: str, indices: ColumnIndices) -> DropRecord:
        """
        Build an instance from the provided raw log and column mapping.

        NOTE: It is currently assumed that the parsed drop log contains all of the necessary
        columns. No error checking is done to account for log files compiled from earlier versions
        of the Dropmate app.
        """
        df = FauxSeries(raw_columns=log_line.split(","), indices=indices)

        return cls(
            serial_number=df["serial_number"],
            uid=df["uid"],
            battery=Health(df["battery"].lower()),
            device_health=Health(df["device_health"].lower()),
            firmware_version=float(df["firmware_version"]),
            flight_index=_try_conv(df["flight_index"], int),
            start_time_utc=_try_conv(df["start_time_utc"], dt.datetime.fromisoformat),
            end_time_utc=_try_conv(df["end_time_utc"], dt.datetime.fromisoformat),
            start_barometric_altitude_msl_ft=_try_conv(df["start_barometric_altitude_msl_ft"], int),
            end_barometric_altitude_msl_ft=_try_conv(df["end_barometric_altitude_msl_ft"], int),
            dropmate_internal_time_utc=dt.datetime.fromisoformat(df["dropmate_internal_time_utc"]),
            last_scanned_time_utc=dt.datetime.fromisoformat(df["last_scanned_time_utc"]),
        )


@dataclass
class Dropmate:  # noqa: D101
    uid: str
    drops: list[DropRecord]
    firmware_version: float
    dropmate_internal_time_utc: dt.datetime
    last_scanned_time_utc: dt.datetime

    def __post_init__(self) -> None:
        # Empty out drops if we have an empty log record
        # An empty Dropmate should only have one record in it
        if self.drops and self.drops[0].flight_index is None:
            self.drops = []

    def __len__(self) -> int:  # pragma: no cover
        return len(self.drops)

    def __str__(self) -> str:  # pragma: no cover
        scanned_pretty = self.last_scanned_time_utc.strftime(r"%Y-%m-%d %H:%M")
        return f"UID: {self.uid}, FW: {self.firmware_version}, {len(self.drops)} drops, Scanned: {scanned_pretty} UTC"  # noqa: E501


def _group_by_uid(drop_logs: abc.Collection[DropRecord]) -> list[Dropmate]:
    # Groupby assumes logs are sorted, so we need to sort them to avoid duplicate devices
    sorted_logs = sorted(drop_logs, key=operator.attrgetter("uid", "flight_index"))
    dropmates = []
    for uid, logs_g in itertools.groupby(sorted_logs, key=operator.attrgetter("uid")):
        logs = list(logs_g)
        dropmates.append(
            Dropmate(
                uid=uid,
                drops=logs,
                # It should be a safe assumption that these values are consistent across logs from
                # the same device
                firmware_version=logs[0].firmware_version,
                dropmate_internal_time_utc=logs[0].dropmate_internal_time_utc,
                last_scanned_time_utc=logs[0].last_scanned_time_utc,
            )
        )

    return dropmates


def _parse_raw_log(log_lines: abc.Sequence[str]) -> list[DropRecord]:
    """
    Parse the provided compiled Dropmate log lines into a list of drop records.

    NOTE: The provided `log_lines` is assumed to include the header line.
    """
    indices = ColumnIndices.from_header(log_lines[0])

    drop_logs = []
    for line in log_lines[1:]:
        drop_logs.append(DropRecord.from_raw(line, indices))

    return drop_logs


def log_parse_pipeline(log_filepath: Path) -> list[Dropmate]:
    """Parse the provided compiled Dropmate log CSV into a list of drops, grouped by device."""
    log_lines = log_filepath.read_text().splitlines()
    parsed_records = _parse_raw_log(log_lines)

    return _group_by_uid(parsed_records)


def merge_dropmates(dropmates: abc.Sequence[Dropmate]) -> list[Dropmate]:
    """Merge a collection of potentially overlapping `Dropmate` devices into a new list."""
    all_drops = set()
    for dropmate in dropmates:
        all_drops.update(dropmate.drops)

    return _group_by_uid(all_drops)
