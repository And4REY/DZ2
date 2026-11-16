from src.domain.repositories import RubricRepository, StudentRepository
from src.domain.rubric import Rubric
from src.domain.student import Student


class InMemoryStudentRepository(StudentRepository):
    def __init__(self) -> None:
        self._students: dict[str, Student] = {}

    def next_id(self) -> str:
        return str(len(self._students) + 1)

    def save(self, student: Student) -> None:
        self._students[student.id] = student

    def get(self, student_id: str) -> Student | None:
        return self._students.get(student_id)

    def all(self) -> list[Student]:
        return list(self._students.values())


class InMemoryRubricRepository(RubricRepository):
    def __init__(self) -> None:
        self._rubric = Rubric()

    def get(self) -> Rubric:
        return self._rubric

    def save(self, rubric: Rubric) -> None:
        self._rubric = rubric
