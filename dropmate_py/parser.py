from __future__ import annotations

import typing as t
from dataclasses import dataclass, fields


@dataclass
class ColumnIndices:
    """
    Column index in the parsed Dropmate compiled log CSV.

    Attribute names are assumed to correspond to the Dropmate log header name. Columns contained may
    vary by Dropmate app version, so if they are not present in the compiled log they will remain at
    a value of `-1`, indicating they were not found.
    """

    serial_number: int = -1
    uid: int = -1
    battery: int = -1
    device_health: int = -1
    firmware_version: int = -1
    start_time_utc: int = -1
    end_time_utc: int = -1
    start_barometric_altitude_msl_ft: int = -1
    end_barometric_altitude_msl_ft: int = -1
    dropmate_internal_time: int = -1
    last_scanned_time: int = -1

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
