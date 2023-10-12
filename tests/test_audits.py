import datetime as dt
from functools import partial

import pytest

from dropmate_py import audits, parser

DATE_P = partial(dt.datetime, year=2023, month=4, day=20, second=0, tzinfo=dt.timezone.utc)

DROPMATE_P = partial(
    parser.Dropmate,
    uid="ABC123",
    drops=[],
    battery=parser.Health.GOOD,
    device_health=parser.Health.GOOD,
    firmware_version=5.1,
    dropmate_internal_time_utc=DATE_P(hour=12, minute=30),
    last_scanned_time_utc=DATE_P(hour=12, minute=30),
)


DROP_RECORD_P = partial(
    parser.DropRecord,
    serial_number="cereal",
    uid="ABC123",
    battery=parser.Health.GOOD,
    device_health=parser.Health.GOOD,
    firmware_version=5.1,
    flight_index=1,
    start_time_utc=DATE_P(hour=11, minute=00),
    end_time_utc=DATE_P(hour=11, minute=30),
    start_barometric_altitude_msl_ft=1000,
    end_barometric_altitude_msl_ft=0,
    dropmate_internal_time_utc=DATE_P(hour=12, minute=30),
    last_scanned_time_utc=DATE_P(hour=12, minute=30),
)

DROP_RECORD_AUDIT_CASES = (
    (DROPMATE_P(), 1),
    (
        DROPMATE_P(
            drops=[
                DROP_RECORD_P(
                    start_barometric_altitude_msl_ft=1000, end_barometric_altitude_msl_ft=0
                )
            ]
        ),
        0,
    ),
    (
        DROPMATE_P(
            drops=[
                DROP_RECORD_P(
                    start_barometric_altitude_msl_ft=1000, end_barometric_altitude_msl_ft=900
                )
            ]
        ),
        1,
    ),
    (
        DROPMATE_P(
            drops=[
                DROP_RECORD_P(
                    start_barometric_altitude_msl_ft=1000, end_barometric_altitude_msl_ft=0
                ),
                DROP_RECORD_P(
                    flight_index=2,
                    start_barometric_altitude_msl_ft=1000,
                    end_barometric_altitude_msl_ft=0,
                ),
            ]
        ),
        0,
    ),
    (
        DROPMATE_P(
            drops=[
                DROP_RECORD_P(
                    start_barometric_altitude_msl_ft=1000, end_barometric_altitude_msl_ft=0
                ),
                DROP_RECORD_P(
                    flight_index=2,
                    start_barometric_altitude_msl_ft=1000,
                    end_barometric_altitude_msl_ft=900,
                ),
            ]
        ),
        1,
    ),
    (
        DROPMATE_P(
            drops=[
                DROP_RECORD_P(
                    start_barometric_altitude_msl_ft=1000, end_barometric_altitude_msl_ft=0
                ),
                DROP_RECORD_P(
                    flight_index=2,
                    start_barometric_altitude_msl_ft=1000,
                    end_barometric_altitude_msl_ft=0,
                    start_time_utc=DATE_P(hour=11, minute=31),
                ),
            ]
        ),
        1,
    ),
)


@pytest.mark.parametrize(("dropmate", "n_expected_errors"), DROP_RECORD_AUDIT_CASES)
def test_audit_drops(dropmate: parser.Dropmate, n_expected_errors: int) -> None:
    reported_errors = audits._audit_drops(
        dropmate=dropmate, min_alt_loss_ft=200, min_delta_to_next_sec=600
    )
    assert len(reported_errors) == n_expected_errors


DROPMATE_AUDIT_CASES = (
    (DROPMATE_P(), 0),
    (DROPMATE_P(firmware_version=1.0), 1),
    (DROPMATE_P(battery=parser.Health.POOR), 1),
    (DROPMATE_P(device_health=parser.Health.POOR), 1),
    (
        DROPMATE_P(
            dropmate_internal_time_utc=DATE_P(hour=14, minute=30),
            last_scanned_time_utc=DATE_P(hour=12, minute=30),
        ),
        1,
    ),
    (
        DROPMATE_P(
            firmware_version=1.0,
            dropmate_internal_time_utc=DATE_P(hour=14, minute=30),
            last_scanned_time_utc=DATE_P(hour=12, minute=30),
        ),
        2,
    ),
)


@pytest.mark.parametrize(("dropmate", "n_expected_errors"), DROPMATE_AUDIT_CASES)
def test_audit_dropmate(dropmate: parser.Dropmate, n_expected_errors: int) -> None:
    reported_errors = audits._audit_dropmate(
        dropmate=dropmate, min_firmware=5.1, max_scanned_time_delta_sec=3600
    )
    assert len(reported_errors) == n_expected_errors


def test_audit_pipeline() -> None:
    dropmates = [
        DROPMATE_P(),
        DROPMATE_P(
            drops=[
                DROP_RECORD_P(
                    start_barometric_altitude_msl_ft=1000, end_barometric_altitude_msl_ft=0
                )
            ]
        ),
        DROPMATE_P(
            drops=[
                DROP_RECORD_P(
                    start_barometric_altitude_msl_ft=1000, end_barometric_altitude_msl_ft=900
                )
            ]
        ),
    ]

    reported_errors = audits.audit_pipeline(
        consolidated_log=dropmates,
        min_alt_loss_ft=200,
        min_firmware=5.1,
        max_scanned_time_delta_sec=3600,
        min_delta_to_next_sec=600,
    )
    assert len(reported_errors) == 2
