from src.application.ports import FinalGradeRow
from src.domain.rubric import Rubric
from src.domain.student import Student
from src.infrastructure.csv_exporter import CsvGradeExporter
from src.infrastructure.memory_repositories import (
    InMemoryRubricRepository,
    InMemoryStudentRepository,
)


def test_student_repository():
    repository = InMemoryStudentRepository()
    student = Student(repository.next_id(), "Иванов")

    repository.save(student)

    assert repository.get("1") is student
    assert repository.get("2") is None
    assert repository.all() == [student]
    assert repository.next_id() == "2"


def test_rubric_repository():
    repository = InMemoryRubricRepository()
    rubric = Rubric()

    repository.save(rubric)

    assert repository.get() is rubric


def test_csv_export(tmp_path):
    path = tmp_path / "grades.csv"
    rows = [FinalGradeRow("1", "Иванов", 7.5), FinalGradeRow("2", "Петрова", 10)]

    CsvGradeExporter().export(rows, str(path))

    lines = path.read_text(encoding="utf-8-sig").splitlines()
    assert lines == ["Номер;Студент;Итог", "1;Иванов;7.50", "2;Петрова;10.00"]
