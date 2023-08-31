from collections import abc

from dropmate_py.audit_errors import (
    AltitudeLossError,
    AuditErrorP,
    EmptyDropLogError,
    InternalClockDeltaError,
    OutdatedFirmwareError,
    TimeDeltaError,
)
from dropmate_py.parser import Dropmate


def _audit_drops(
    dropmate: Dropmate,
    min_alt_loss_ft: int,
    min_delta_to_next_sec: int,
) -> list[AuditErrorP]:
    """
    Audit the drop records for the provided Dropmate.

    Dropmate is audited for the following issues:
        * Empty drop records
        * Altitude loss below the provided threshold
        * For Dropmates with more than one record, check that the beginning of the drop record is
        far enough away from the end of the previous record, which may indicate that a drop has been
        double counted
    """
    found_issues: list[AuditErrorP] = []

    if len(dropmate.drops) == 0:
        found_issues.append(EmptyDropLogError(dropmate))
        return found_issues

    # Once we've gotten here then we've already exited on an empty log so we can't have any None
    # values in our DropRecords

    for drop_record in dropmate.drops:
        start = drop_record.start_barometric_altitude_msl_ft
        end = drop_record.end_barometric_altitude_msl_ft
        altitude_loss = start - end  # type: ignore[operator]
        if altitude_loss < min_alt_loss_ft:
            found_issues.append(AltitudeLossError(dropmate, drop_record, altitude_loss))

    # Check for log start timestamps that are in close proximity to the end of the previous log,
    # indicating that a jump may have ended prematurely
    # We shouldn't have enough records where performance is critical, so we can just do a new loop
    # rather than complicating the altitude checking one
    for prev_rec, next_rec in zip(dropmate.drops, dropmate.drops[1:]):
        next_start = next_rec.start_time_utc
        prev_end = prev_rec.end_time_utc
        start_delta = (next_start - prev_end).total_seconds()  # type: ignore[operator]
        if abs(start_delta) < min_delta_to_next_sec:
            found_issues.append(TimeDeltaError(dropmate, next_rec, start_delta))

    return found_issues


def _audit_dropmate(
    dropmate: Dropmate,
    min_firmware: float,
    max_scanned_time_delta_sec: int,
) -> list[AuditErrorP]:
    """Audit for issues with firmware version and delta between internal and external clocks."""
    found_issues: list[AuditErrorP] = []

    if dropmate.firmware_version < min_firmware:
        found_issues.append(OutdatedFirmwareError(dropmate))

    internal_timedelta = dropmate.last_scanned_time_utc - dropmate.dropmate_internal_time_utc
    if abs(internal_timedelta.total_seconds()) > max_scanned_time_delta_sec:
        found_issues.append(InternalClockDeltaError(dropmate, internal_timedelta.total_seconds()))

    return found_issues


def audit_pipeline(
    consolidated_log: abc.Iterable[Dropmate],
    min_alt_loss_ft: int,
    min_delta_to_next_sec: int,
    min_firmware: float,
    max_scanned_time_delta_sec: int,
) -> list[AuditErrorP]:
    """Run the desired audits over all Dropmate devices and their respective drop records."""
    found_issues: list[AuditErrorP] = []

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
