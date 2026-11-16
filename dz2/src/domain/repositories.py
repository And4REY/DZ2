from abc import ABC, abstractmethod

from src.domain.rubric import Rubric
from src.domain.student import Student


class StudentRepository(ABC):
    @abstractmethod
    def next_id(self) -> str:
        pass

    @abstractmethod
    def save(self, student: Student) -> None:
        pass

    @abstractmethod
    def get(self, student_id: str) -> Student | None:
        pass

    @abstractmethod
    def all(self) -> list[Student]:
        pass


class RubricRepository(ABC):
    @abstractmethod
    def get(self) -> Rubric:
        pass

    @abstractmethod
    def save(self, rubric: Rubric) -> None:
        pass
