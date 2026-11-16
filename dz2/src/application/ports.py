from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class FinalGradeRow:
    student_id: str
    name: str
    grade: float


class GradeExporter(ABC):
    @abstractmethod
    def export(self, rows: list[FinalGradeRow], destination: str) -> None:
        pass
