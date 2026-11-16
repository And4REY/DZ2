import math
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Score:
    value: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.value):
            raise ValueError("Балл должен быть числом")
        if self.value < 0:
            raise ValueError("Балл не может быть отрицательным")


@dataclass(frozen=True)
class Evaluation:
    criterion_id: str
    score: Score
    graded_on: date
    comment: str = ""
