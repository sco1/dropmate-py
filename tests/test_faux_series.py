import pytest

from dropmate_py import parser

SAMPLE_FULL_HEADER = "serial_number,uid,battery,device_health,firmware_version,log_timestamp,log_altitude,total_flights,flights_over_18kft,recorded_flights,flight_index,start_time_utc,end_time_utc,start_barometric_altitude_msl_ft,end_barometric_altitude_msl_ft,dropmate_internal_time_utc,last_scanned_time_utc,scan_device_type,scan_device_os,dropmate_app_version"
SAMPLE_DATA_LINE = "0,E002270067A94C18,Good,good,5.1,true,true,3,0,3,1,2023-04-20T14:45:45Z,2023-04-20T14:47:37Z,1591,262,2023-04-20T19:16:38Z,2023-04-20T19:34:04.547Z,SM S901U1,31,1.5.16"

SAMPLE_FULL_HEADER_COL_IDX = parser.ColumnIndices.from_header(SAMPLE_FULL_HEADER)


def test_faux_series_getter() -> None:
    ds = parser.FauxSeries(SAMPLE_DATA_LINE.split(","), SAMPLE_FULL_HEADER_COL_IDX)
    assert ds["uid"] == "E002270067A94C18"


SAMPLE_SHORT_HEADER = "serial_number,uid,battery,log_timestamp,log_altitude,total_flights,prior_flights,flights_over_18kft,recorded_flights,flight_index,start_time_utc,end_time_utc,start_barometric_altitude_msl_ft,end_barometric_altitude_msl_ft"
SAMPLE_SHORT_DATA_LINE = (
    "5,E00227006796B05F,Good,on,on,7,0,0,7,1,2023-Apr-20T14-48-53Z,2023-Apr-20T14-56-07Z,5364,1444"
)

SAMPLE_SHORT_HEADER_COL_IDX = parser.ColumnIndices.from_header(SAMPLE_SHORT_HEADER)


def test_faux_series_getter_old_log_raises() -> None:
    ds = parser.FauxSeries(SAMPLE_SHORT_DATA_LINE.split(","), SAMPLE_SHORT_HEADER_COL_IDX)

    with pytest.raises(KeyError):
        _ = ds["device_health"]
