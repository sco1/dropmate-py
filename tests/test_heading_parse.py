from dropmate_py.parser import ColumnIndices

SAMPLE_FULL_HEADER = "serial_number,uid,battery,device_health,firmware_version,log_timestamp,log_altitude,total_flights,flights_over_18kft,recorded_flights,flight_index,start_time_utc,end_time_utc,start_barometric_altitude_msl_ft,end_barometric_altitude_msl_ft,dropmate_internal_time_utc,last_scanned_time_utc,scan_device_type,scan_device_os,dropmate_app_version"


def test_parse_indices_full_header() -> None:
    TRUTH_INDICES = ColumnIndices(
        serial_number=0,
        uid=1,
        battery=2,
        device_health=3,
        firmware_version=4,
        log_timestamp=5,
        log_altitude=6,
        total_flights=7,
        flights_over_18kft=8,
        recorded_flights=9,
        flight_index=10,
        start_time_utc=11,
        end_time_utc=12,
        start_barometric_altitude_msl_ft=13,
        end_barometric_altitude_msl_ft=14,
        dropmate_internal_time_utc=15,
        last_scanned_time_utc=16,
        scan_device_type=17,
        scan_device_os=18,
        dropmate_app_version=19,
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
        log_timestamp=3,
        log_altitude=4,
        total_flights=5,
        flights_over_18kft=7,
        recorded_flights=8,
        flight_index=9,
        start_time_utc=10,
        end_time_utc=11,
        start_barometric_altitude_msl_ft=12,
        end_barometric_altitude_msl_ft=13,
        dropmate_internal_time_utc=-1,
        last_scanned_time_utc=-1,
        scan_device_type=-1,
        scan_device_os=-1,
        dropmate_app_version=-1,
    )

    indices = ColumnIndices.from_header(SAMPLE_OLD_HEADER)
    assert indices == TRUTH_INDICES
