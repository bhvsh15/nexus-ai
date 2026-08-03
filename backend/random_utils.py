from dataclasses import dataclass
from pathlib import Path


def ensure_suffix(filename: str, suffix: str) -> str:
    if filename.endswith(suffix):
        return filename
    return f"{filename}{suffix}"


def count_lines(text: str) -> int:
    return len([line for line in text.splitlines() if line.strip()])


@dataclass
class FileSummary:
    path: Path
    lines: int = 0

    def describe(self) -> str:
        return f"{self.path.name}: {self.lines} lines"


class PathBuilder:
    def __init__(self, base: Path) -> None:
        self.base = base

    def child(self, name: str) -> Path:
        return self.base / name

