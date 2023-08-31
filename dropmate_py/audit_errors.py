import typing as t

from dropmate_py.parser import DropRecord, Dropmate


class AuditErrorBase(Exception):
    pass


class AuditErrorP(t.Protocol):
    def __str__(self) -> str:
        ...


class DropmateAuditErrorBase(AuditErrorBase):
    def __init__(self, device: Dropmate):
        self.device = device


class EmptyDropLogError(DropmateAuditErrorBase):
    def __str__(self) -> str:
        return f"UID {self.device.uid} contains no drop records."


class OutdatedFirmwareError(DropmateAuditErrorBase):
    def __str__(self) -> str:
        return f"UID {self.device.uid} firmware below threshold: {self.device.firmware_version}"


class InternalClockDeltaError(DropmateAuditErrorBase):
    def __init__(self, device: Dropmate, val: float) -> None:
        self.device = device
        self.val = val

    def __str__(self) -> str:
        return f"UID {self.device.uid} internal time delta from scanned time exceeds threshold: {self.val} seconds"


class DropRecordError(AuditErrorBase):
    def __init__(self, device: Dropmate, drop_record: DropRecord, val: float) -> None:
        self.device = device
        self.drop_record = drop_record
        self.val = val


class AltitudeLossError(DropRecordError):
    def __str__(self) -> str:
        return f"UID {self.device.uid} drop #{self.drop_record.flight_index} below threshold altitude loss: {self.val} feet"


class TimeDeltaError(DropRecordError):
    def __str__(self) -> str:
        return f"UID {self.device.uid} drop #{self.drop_record.flight_index} start time below threshold from previous flight: {self.val} seconds"
