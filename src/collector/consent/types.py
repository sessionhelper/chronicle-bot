from enum import StrEnum


class SessionState(StrEnum):
    IDLE = "idle"
    AWAITING_CONSENT = "awaiting_consent"
    RECORDING = "recording"
    FINALIZING = "finalizing"
    UPLOADING = "uploading"
    COMPLETE = "complete"
    CANCELLED = "cancelled"


class ConsentScope(StrEnum):
    FULL = "full"  # audio included in dataset
    DECLINE_AUDIO = "decline_audio"  # stays in voice, not recorded
    DECLINE = "decline"  # full decline
