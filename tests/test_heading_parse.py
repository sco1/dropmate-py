from dropmate_py.parser import ColumnIndices

SAMPLE_FULL_HEADER = "serial_number,uid,battery,device_health, firmware_version,log_timestamp,log_altitude,total_flights,flights_over_18kft,recorded_flights,flight_index,start_time_utc,end_time_utc,start_barometric_altitude_msl_ft,end_barometric_altitude_msl_ft,dropmate_internal_time,last_scanned_time"


def test_parse_indices_full_header() -> None:
    TRUTH_INDICES = ColumnIndices(
        serial_number=0,
        uid=1,
        battery=2,
        device_health=3,
        firmware_version=4,
        start_time_utc=11,
        end_time_utc=12,
        start_barometric_altitude_msl_ft=13,
        end_barometric_altitude_msl_ft=14,
        dropmate_internal_time=15,
        last_scanned_time=16,
    )

    indices = ColumnIndices.from_header(SAMPLE_FULL_HEADER)
    assert indices == TRUTH_INDICES


SAMPLE_OLD_HEADER = "serial_number,uid,battery,log_timestamp,log_altitude,total_flights,prior_flights,flights_over_18kft,recorded_flights,flight_index,start_time_utc,end_time_utc,start_barometric_altitude_msl_ft,end_barometric_altitude_msl_ft"


def test_parse_indices_old_header() -> None:
    TRUTH_INDICES = ColumnIndices(
        serial_number=0,
        uid=1,
        battery=2,
        device_health=-1,
        firmware_version=-1,
        start_time_utc=10,
        end_time_utc=11,
        start_barometric_altitude_msl_ft=12,
        end_barometric_altitude_msl_ft=13,
        dropmate_internal_time=-1,
        last_scanned_time=-1,
    )

    indices = ColumnIndices.from_header(SAMPLE_OLD_HEADER)
    assert indices == TRUTH_INDICES
