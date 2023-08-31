from collections import abc

from dropmate_py.parser import Dropmate


def _audit_drops(dropmate: Dropmate, min_alt_loss_ft: int) -> list[str]:
    """Audit for missing drop records and for issues with total altitude loss."""
    found_issues = []

    if len(dropmate.drops) == 0:
        found_issues.append(f"UID {dropmate.uid} contains no drop records.")
        return found_issues

    for drop_record in dropmate.drops:
        # Type guard, we should have already returned early before we get to an empty drop record
        if (
            drop_record.start_barometric_altitude_msl_ft is None
            or drop_record.end_barometric_altitude_msl_ft is None
        ):
            continue  # pragma: no cover

        altitude_loss = (
            drop_record.start_barometric_altitude_msl_ft
            - drop_record.end_barometric_altitude_msl_ft
        )
        if altitude_loss < min_alt_loss_ft:
            found_issues.append(
                f"UID {dropmate.uid} drop #{drop_record.flight_index} below threshold altitude loss: {altitude_loss} feet."  # noqa: E501
            )

    return found_issues


def _audit_dropmate(
    dropmate: Dropmate, min_firmware: float, max_scanned_time_delta_sec: int
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
        found_issues.extend(_audit_drops(dropmate, min_alt_loss_ft=min_alt_loss_ft))

    return found_issues
