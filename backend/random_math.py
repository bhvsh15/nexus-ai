from dataclasses import dataclass


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def percent(part: float, whole: float) -> float:
    if whole == 0:
        return 0.0
    return (part / whole) * 100.0


@dataclass
class RollingAverage:
    values: list[float]

    def add(self, value: float) -> None:
        self.values.append(value)

    def value(self) -> float:
        if not self.values:
            return 0.0
        return sum(self.values) / len(self.values)


class RangeTracker:
    def __init__(self) -> None:
        self.minimum: float | None = None
        self.maximum: float | None = None

    def update(self, value: float) -> None:
        self.minimum = value if self.minimum is None else min(self.minimum, value)
        self.maximum = value if self.maximum is None else max(self.maximum, value)

