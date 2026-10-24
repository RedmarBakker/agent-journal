import traceback
from pathlib import Path

REPOSITORY_FOLDER = str(Path(__file__).parent)


class ReadCaller:
    """The file and line of the code outside the repositories that asked for a read."""

    @staticmethod
    def found() -> str:
        frame = next((frame for frame in reversed(traceback.extract_stack()) if not frame.filename.startswith(REPOSITORY_FOLDER) and "/db/" not in frame.filename), None)
        return f"{Path(frame.filename).name}:{frame.lineno}" if frame else "unknown"
