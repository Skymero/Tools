"""Portable single-process lock based on exclusive file creation."""
from pathlib import Path


class AlreadyRunningError(RuntimeError): pass


class ProcessLock:
    def __init__(self, path): self.path, self.stream = Path(path), None
    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try: self.stream = self.path.open("x", encoding="ascii")
        except FileExistsError as exc: raise AlreadyRunningError("another queue process is running") from exc
        self.stream.write(str(__import__('os').getpid())); self.stream.flush(); return self
    def __exit__(self, *_):
        self.stream.close(); self.path.unlink(missing_ok=True)
