import os

# @sin ParentPidVariableDetector
PARENT_VARIABLE = "JOURNAL_PARENT_PID"


def parent_number() -> int:
    # @sin ParentPidWatchDetector
    return os.getppid()


def process_number() -> int:
    # @righteous ParentPidWatchDetector
    return os.getpid()
