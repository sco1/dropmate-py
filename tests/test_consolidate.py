from pathlib import Path
from textwrap import dedent

from dropmate_py.log_utils import consolidate_drop_records

SAMPLE_LOG_NEW_HEADER = dedent(
    """\
    serial_number,uid,battery,device_health,firmware_version,log_timestamp,log_altitude,total_flights,flights_over_18kft,recorded_flights,flight_index,start_time_utc,end_time_utc,start_barometric_altitude_msl_ft,end_barometric_altitude_msl_ft,dropmate_internal_time_utc,last_scanned_time_utc,scan_device_type,scan_device_os,dropmate_app_version
    0,abc123,Good,good,5.1,true,true,3,0,3,1,2023-04-20T15:24:00Z,2023-04-20T15:25:00Z,1500,300,2023-04-20T16:13:01Z,2023-04-20T16:13:31.061Z,SM S901U1,31,1.5.16
    0,abc123,Good,good,5.1,true,true,3,0,3,2,2023-04-20T16:18:00Z,2023-04-20T16:19:00Z,1400,200,2023-04-20T16:13:01Z,2023-04-20T16:13:31.061Z,SM S901U1,31,1.5.16
    0,abc123,Good,good,5.1,true,true,3,0,3,3,2023-04-20T16:20:00Z,2023-04-20T16:21:00Z,1300,100,2023-04-20T16:13:01Z,2023-04-20T16:13:31.061Z,SM S901U1,31,1.5.16
    """
)

SAMPLE_LOG_LEGACY_HEADER = dedent(
    """\
    serial_number,uid,battery,device_health, firmware_version,log_timestamp,log_altitude,total_flights,flights_over_18kft,recorded_flights,flight_index,start_time_utc,end_time_utc,start_barometric_altitude_msl_ft,end_barometric_altitude_msl_ft,dropmate_internal_time,last_scanned_time
    0,abc123,good,good,5.1,on,on,1,0,1,1,2023-04-20T15:24:00Z,2023-04-20T15:25:00Z,1500,300,2023-04-20T18:09:28Z,2023-04-20T18:17:12Z
    0,abc456,good,good,5.1,on,on,1,0,1,1,2023-04-20T14:53:00Z,2023-04-20T14:55:00Z,1500,200,2023-04-20T18:13:18Z,2023-04-20T18:16:56Z
    """
)

TRUTH_CONSOLIDATED = dedent(
    """\
    uid,flight_index,start_time_utc,end_time_utc,start_barometric_altitude_msl_ft,end_barometric_altitude_msl_ft
    abc123,1,2023-04-20T15:24:00Z,2023-04-20T15:25:00Z,1500,300
    abc123,2,2023-04-20T16:18:00Z,2023-04-20T16:19:00Z,1400,200
    abc123,3,2023-04-20T16:20:00Z,2023-04-20T16:21:00Z,1300,100
    abc456,1,2023-04-20T14:53:00Z,2023-04-20T14:55:00Z,1500,200
    """
)


def test_consolidate_drop_records(tmp_path: Path) -> None:
    new_header_log = tmp_path / "dropmate_records_new_header.csv"
    new_header_log.write_text(SAMPLE_LOG_NEW_HEADER)

    legacy_header_log = tmp_path / "dropmate_records_legacy_header.csv"
    legacy_header_log.write_text(SAMPLE_LOG_LEGACY_HEADER)

    out_log = tmp_path / "out_log.csv"
    consolidate_drop_records(tmp_path, log_pattern="dropmate_records_*", out_filepath=out_log)

    assert out_log.exists()

    out_data = out_log.read_text()
    assert out_data == TRUTH_CONSOLIDATED


SAMPLE_LOG_TEN_RECORDS = dedent(
    """\
    serial_number,uid,battery,device_health,firmware_version,log_timestamp,log_altitude,total_flights,flights_over_18kft,recorded_flights,flight_index,start_time_utc,end_time_utc,start_barometric_altitude_msl_ft,end_barometric_altitude_msl_ft,dropmate_internal_time_utc,last_scanned_time_utc,scan_device_type,scan_device_os,dropmate_app_version
    0,ABC123,Good,good,5.0,true,true,12,0,12,1,2023-04-20T13:00:00Z,2023-04-20T13:00:00Z,10000,0,2023-04-20T14:00:00Z,2023-04-20T14:00:00.003Z,SM G965U1,29,1.5.16
    0,ABC123,Good,good,5.0,true,true,12,0,12,2,2023-04-20T16:00:00Z,2023-04-20T16:00:00Z,10000,0,2023-04-20T14:00:00Z,2023-04-20T14:00:00.003Z,SM G965U1,29,1.5.16
    0,ABC123,Good,good,5.0,true,true,12,0,12,3,2023-04-20T14:00:00Z,2023-04-20T14:00:00Z,10000,0,2023-04-20T14:00:00Z,2023-04-20T14:00:00.003Z,SM G965U1,29,1.5.16
    0,ABC123,Good,good,5.0,true,true,12,0,12,4,2023-04-20T16:00:00Z,2023-04-20T16:00:00Z,10000,0,2023-04-20T14:00:00Z,2023-04-20T14:00:00.003Z,SM G965U1,29,1.5.16
    0,ABC123,Good,good,5.0,true,true,12,0,12,5,2023-04-20T18:00:00Z,2023-04-20T18:00:00Z,10000,0,2023-04-20T14:00:00Z,2023-04-20T14:00:00.003Z,SM G965U1,29,1.5.16
    0,ABC123,Good,good,5.0,true,true,12,0,12,6,2023-04-20T14:00:00Z,2023-04-20T14:00:00Z,10000,0,2023-04-20T14:00:00Z,2023-04-20T14:00:00.003Z,SM G965U1,29,1.5.16
    0,ABC123,Good,good,5.0,true,true,12,0,12,7,2023-04-20T13:00:00Z,2023-04-20T14:00:00Z,10000,0,2023-04-20T14:00:00Z,2023-04-20T14:00:00.003Z,SM G965U1,29,1.5.16
    0,ABC123,Good,good,5.0,true,true,12,0,12,8,2023-04-20T18:00:00Z,2023-04-20T18:00:00Z,10000,0,2023-04-20T14:00:00Z,2023-04-20T14:00:00.003Z,SM G965U1,29,1.5.16
    0,ABC123,Good,good,5.0,true,true,12,0,12,9,2023-04-20T16:00:00Z,2023-04-20T16:00:00Z,10000,0,2023-04-20T14:00:00Z,2023-04-20T14:00:00.003Z,SM G965U1,29,1.5.16
    0,ABC123,Good,good,5.0,true,true,12,0,12,10,2023-04-20T13:00:00Z,2023-04-20T13:00:00Z,1000,0,2023-04-20T14:00:00Z,2023-04-20T14:00:00.003Z,SM G965U1,29,1.5.16
    """
)

TRUTH_CONSOLIDATED_TEN_RECORDS = [
    "ABC123,1,2023-04-20T13:00:00Z,2023-04-20T13:00:00Z,10000,0",
    "ABC123,2,2023-04-20T16:00:00Z,2023-04-20T16:00:00Z,10000,0",
    "ABC123,3,2023-04-20T14:00:00Z,2023-04-20T14:00:00Z,10000,0",
    "ABC123,4,2023-04-20T16:00:00Z,2023-04-20T16:00:00Z,10000,0",
    "ABC123,5,2023-04-20T18:00:00Z,2023-04-20T18:00:00Z,10000,0",
    "ABC123,6,2023-04-20T14:00:00Z,2023-04-20T14:00:00Z,10000,0",
    "ABC123,7,2023-04-20T13:00:00Z,2023-04-20T14:00:00Z,10000,0",
    "ABC123,8,2023-04-20T18:00:00Z,2023-04-20T18:00:00Z,10000,0",
    "ABC123,9,2023-04-20T16:00:00Z,2023-04-20T16:00:00Z,10000,0",
    "ABC123,10,2023-04-20T13:00:00Z,2023-04-20T13:00:00Z,1000,0",
]


def test_consolidated_record_sorting(tmp_path: Path) -> None:
    sample_log = tmp_path / "dropmate_records_ten_records.csv"
    sample_log.write_text(SAMPLE_LOG_TEN_RECORDS)

    consolidated = consolidate_drop_records(
        tmp_path, log_pattern="dropmate_records_*", out_filepath=Path(), write_file=False
    )
    assert consolidated == TRUTH_CONSOLIDATED_TEN_RECORDS
