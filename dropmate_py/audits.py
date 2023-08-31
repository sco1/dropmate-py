from collections import abc

from dropmate_py.parser import Dropmate


def _audit_drops(
    dropmate: Dropmate,
    min_alt_loss_ft: int,
    min_delta_to_next_sec: int,
) -> list[str]:
    """
    Audit the drop records for the provided Dropmate.

    Dropmate is audited for the following issues:
        * Empty drop records
        * Altitude loss below the provided threshold
        * For Dropmates with more than one record, check that the beginning of the drop record is
        far enough away from the end of the previous record, which may indicate that a drop has been
        double counted
    """
    found_issues = []

    if len(dropmate.drops) == 0:
        found_issues.append(f"UID {dropmate.uid} contains no drop records.")
        return found_issues

    # Once we've gotten here then we've already exited on an empty log so we can't have any None
    # values in our DropRecords

    for drop_record in dropmate.drops:
        start = drop_record.start_barometric_altitude_msl_ft
        end = drop_record.end_barometric_altitude_msl_ft
        altitude_loss = start - end  # type: ignore[operator]
        if altitude_loss < min_alt_loss_ft:
            found_issues.append(
                f"UID {dropmate.uid} drop #{drop_record.flight_index} below threshold altitude loss: {altitude_loss} feet."  # noqa: E501
            )

    # Check for log start timestamps that are in close proximity to the end of the previous log,
    # indicating that a jump may have ended prematurely
    # We shouldn't have enough records where performance is critical, so we can just do a new loop
    # rather than complicating the altitude checking one
    for prev_rec, next_rec in zip(dropmate.drops, dropmate.drops[1:]):
        next_start = next_rec.start_time_utc
        prev_end = prev_rec.end_time_utc
        start_delta = (next_start - prev_end).total_seconds()  # type: ignore[operator]
        if abs(start_delta) < min_delta_to_next_sec:
            found_issues.append(
                f"UID {dropmate.uid} drop #{next_rec.flight_index} start time below threshold from previous flight: {start_delta} seconds"  # noqa: E501
            )

    return found_issues


def _audit_dropmate(
    dropmate: Dropmate,
    min_firmware: float,
    max_scanned_time_delta_sec: int,
) -> list[str]:
    """Audit for issues with firmware version and delta between internal and external clocks."""
    found_issues = []

    if dropmate.firmware_version < min_firmware:
        found_issues.append(
            f"UID {dropmate.uid} firmware below threshold: {dropmate.firmware_version}"
        )

    internal_timedelta = dropmate.last_scanned_time_utc - dropmate.dropmate_internal_time_utc
    if abs(internal_timedelta.total_seconds()) > max_scanned_time_delta_sec:
        found_issues.append(
            f"UID {dropmate.uid} internal time delta from scanned time exceeds threshold: {internal_timedelta.total_seconds()} seconds"  # noqa: E501
        )

    return found_issues


def audit_pipeline(
    consolidated_log: abc.Iterable[Dropmate],
    min_alt_loss_ft: int,
    min_delta_to_next_sec: int,
    min_firmware: float,
    max_scanned_time_delta_sec: int,
) -> list[str]:
    """Run the desired audits over all Dropmate devices and their respective drop records."""
    found_issues = []

    for dropmate in consolidated_log:
        found_issues.extend(
            _audit_dropmate(
                dropmate,
                min_firmware=min_firmware,
                max_scanned_time_delta_sec=max_scanned_time_delta_sec,
            )
        )
        found_issues.extend(
            _audit_drops(
                dropmate,
                min_alt_loss_ft=min_alt_loss_ft,
                min_delta_to_next_sec=min_delta_to_next_sec,
            )
        )

    return found_issues
