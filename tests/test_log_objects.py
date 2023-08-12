import datetime as dt
from dataclasses import fields
from functools import partial
from pathlib import Path
from textwrap import dedent

import pytest

from dropmate_py import parser

DROP_RECORD_P = partial(
    parser.DropRecord,
    serial_number="cereal",
    battery=parser.Health.GOOD,
    device_health=parser.Health.GOOD,
    firmware_version=5.1,
    flight_index=1,
    start_time_utc=dt.datetime(
        year=2023, month=4, day=20, hour=11, minute=00, second=0, tzinfo=dt.timezone.utc
    ),
    end_time_utc=dt.datetime(
        year=2023, month=4, day=20, hour=11, minute=30, second=0, tzinfo=dt.timezone.utc
    ),
    start_barometric_altitude_msl_ft=1000,
    end_barometric_altitude_msl_ft=0,
    dropmate_internal_time_utc=dt.datetime(
        year=2023, month=4, day=20, hour=12, minute=30, second=0, tzinfo=dt.timezone.utc
    ),
    last_scanned_time_utc=dt.datetime(
        year=2023, month=4, day=20, hour=12, minute=30, second=0, tzinfo=dt.timezone.utc
    ),
)

SAMPLE_FULL_HEADER = "serial_number,uid,battery,device_health,firmware_version,log_timestamp,log_altitude,total_flights,flights_over_18kft,recorded_flights,flight_index,start_time_utc,end_time_utc,start_barometric_altitude_msl_ft,end_barometric_altitude_msl_ft,dropmate_internal_time_utc,last_scanned_time_utc,scan_device_type,scan_device_os,dropmate_app_version"
SAMPLE_DATA_LINE = "cereal,ABC123,Good,good,5.1,true,true,3,0,3,1,2023-04-20T11:00:00Z,2023-04-20T11:30:00Z,1000,0,2023-04-20T12:30:00Z,2023-04-20T12:30:00Z,SM S901U1,31,1.5.16"

SAMPLE_FULL_HEADER_COL_IDX = parser.ColumnIndices.from_header(SAMPLE_FULL_HEADER)


def test_droprecord_from_raw() -> None:
    truth_log = DROP_RECORD_P(
        uid="ABC123",
        flight_index=1,
    )

    log = parser.DropRecord.from_raw(SAMPLE_DATA_LINE, SAMPLE_FULL_HEADER_COL_IDX)

    for i in fields(truth_log):
        left = getattr(log, i.name)
        right = getattr(truth_log, i.name)
        assert left == right, f"Mismatch for field {i.name}"


LOG_EQUALITY_TEST_CASES = (
    (
        DROP_RECORD_P(uid="ABC123", flight_index=1),
        DROP_RECORD_P(uid="ABC123", flight_index=1),
        True,
    ),
    (
        DROP_RECORD_P(uid="ABC123", flight_index=1),
        DROP_RECORD_P(uid="ABC123", flight_index=2),
        False,
    ),
    (
        DROP_RECORD_P(uid="ABC123", flight_index=1),
        DROP_RECORD_P(uid="ABC1234", flight_index=1),
        False,
    ),
)


@pytest.mark.parametrize(("left", "right", "truth_eq"), LOG_EQUALITY_TEST_CASES)
def test_drop_log_equality(
    left: parser.DropRecord, right: parser.DropRecord, truth_eq: bool
) -> None:
    assert (left == right) == truth_eq
    assert (hash(left) == hash(right)) == truth_eq


def test_drop_log_equality_non_droplog_raises() -> None:
    log = DROP_RECORD_P(
        uid="ABC123",
        start_time_utc=dt.datetime(
            year=2023, month=4, day=20, hour=11, minute=00, second=0, tzinfo=dt.timezone.utc
        ),
    )

    with pytest.raises(NotImplementedError):
        log == "foo"  # noqa: B015


SAMPLE_CONSOLIDATED_LOG = dedent(
    """\
    serial_number,uid,battery,device_health,firmware_version,log_timestamp,log_altitude,total_flights,flights_over_18kft,recorded_flights,flight_index,start_time_utc,end_time_utc,start_barometric_altitude_msl_ft,end_barometric_altitude_msl_ft,dropmate_internal_time_utc,last_scanned_time_utc,scan_device_type,scan_device_os,dropmate_app_version
    cereal,A1,Good,good,5.1,true,true,3,0,3,1,2023-04-20T11:00:00Z,2023-04-20T11:30:00Z,1000,0,2023-04-20T12:30:00Z,2023-04-20T12:30:00Z,SM S901U1,31,1.5.16
    cereal,A1,Good,good,5.1,true,true,3,0,3,3,2023-04-20T11:00:00Z,2023-04-20T11:30:00Z,1000,0,2023-04-20T12:30:00Z,2023-04-20T12:30:00Z,SM S901U1,31,1.5.16
    cereal,A2,Good,good,5.1,true,true,3,0,3,1,2023-04-20T11:00:00Z,2023-04-20T11:30:00Z,1000,0,2023-04-20T12:30:00Z,2023-04-20T12:30:00Z,SM S901U1,31,1.5.16
    cereal,A2,Good,good,5.1,true,true,3,0,3,3,2023-04-20T11:00:00Z,2023-04-20T11:30:00Z,1000,0,2023-04-20T12:30:00Z,2023-04-20T12:30:00Z,SM S901U1,31,1.5.16
    cereal,A3,Good,good,5.1,true,true,2,0,2,1,2023-04-20T11:00:00Z,2023-04-20T11:30:00Z,1000,0,2023-04-20T12:30:00Z,2023-04-20T12:30:00Z,SM S901U1,31,1.5.16
    """
)


def test_log_line_parse() -> None:
    log_lines = SAMPLE_CONSOLIDATED_LOG.splitlines()
    parsed_records = parser._parse_raw_log(log_lines)

    assert len(parsed_records) == 5


def test_group_by_uid() -> None:
    log_lines = SAMPLE_CONSOLIDATED_LOG.splitlines()
    parsed_records = parser._parse_raw_log(log_lines)

    grouped_records = parser._group_by_uid(parsed_records)
    assert len(grouped_records) == 3
    assert [rec.uid for rec in grouped_records] == ["A1", "A2", "A3"]


SAMPLE_CONSOLIDATED_LOG_UNSORTED = dedent(
    """\
    serial_number,uid,battery,device_health,firmware_version,log_timestamp,log_altitude,total_flights,flights_over_18kft,recorded_flights,flight_index,start_time_utc,end_time_utc,start_barometric_altitude_msl_ft,end_barometric_altitude_msl_ft,dropmate_internal_time_utc,last_scanned_time_utc,scan_device_type,scan_device_os,dropmate_app_version
    cereal,A3,Good,good,5.1,true,true,2,0,2,1,2023-04-20T11:00:00Z,2023-04-20T11:30:00Z,1000,0,2023-04-20T12:30:00Z,2023-04-20T12:30:00Z,SM S901U1,31,1.5.16
    cereal,A1,Good,good,5.1,true,true,3,0,3,1,2023-04-20T11:00:00Z,2023-04-20T11:30:00Z,1000,0,2023-04-20T12:30:00Z,2023-04-20T12:30:00Z,SM S901U1,31,1.5.16
    cereal,A2,Good,good,5.1,true,true,3,0,3,1,2023-04-20T11:00:00Z,2023-04-20T11:30:00Z,1000,0,2023-04-20T12:30:00Z,2023-04-20T12:30:00Z,SM S901U1,31,1.5.16
    cereal,A1,Good,good,5.1,true,true,3,0,3,3,2023-04-20T11:00:00Z,2023-04-20T11:30:00Z,1000,0,2023-04-20T12:30:00Z,2023-04-20T12:30:00Z,SM S901U1,31,1.5.16
    cereal,A2,Good,good,5.1,true,true,3,0,3,3,2023-04-20T11:00:00Z,2023-04-20T11:30:00Z,1000,0,2023-04-20T12:30:00Z,2023-04-20T12:30:00Z,SM S901U1,31,1.5.16
    """
)


def test_unsorted_group_by_uid() -> None:
    log_lines = SAMPLE_CONSOLIDATED_LOG_UNSORTED.splitlines()
    parsed_records = parser._parse_raw_log(log_lines)

    grouped_records = parser._group_by_uid(parsed_records)
    assert len(grouped_records) == 3


def test_file_parse_pipeline(tmp_path: Path) -> None:
    log_file = tmp_path / "compiled.CSV"
    log_file.write_text(SAMPLE_CONSOLIDATED_LOG)

    grouped_records = parser.log_parse_pipeline(log_file)
    assert len(grouped_records) == 3
    assert [rec.uid for rec in grouped_records] == ["A1", "A2", "A3"]


def test_merge_dropomates() -> None:
    faux_batch_dropmates = parser._group_by_uid(
        parser._parse_raw_log(SAMPLE_CONSOLIDATED_LOG.splitlines())
    )
    faux_batch_dropmates.extend(
        parser._group_by_uid(parser._parse_raw_log(SAMPLE_CONSOLIDATED_LOG.splitlines()))
    )

    merged = parser.merge_dropmates(faux_batch_dropmates)
    assert len(merged) == 3
