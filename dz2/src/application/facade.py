from src.application.ports import FinalGradeRow, GradeExporter
from src.domain.evaluation_factory import EvaluationFactory
from src.domain.grading import FinalGradeCalculator, FinalGradeRule
from src.domain.repositories import RubricRepository, StudentRepository
from src.domain.rubric import Criterion
from src.domain.student import Student
from src.domain.values import Evaluation


class PosFacade:
    def __init__(
        self,
        students: StudentRepository,
        rubrics: RubricRepository,
        factory: EvaluationFactory,
        calculator: FinalGradeCalculator,
        exporter: GradeExporter,
    ) -> None:
        self._students = students
        self._rubrics = rubrics
        self._factory = factory
        self._calculator = calculator
        self._exporter = exporter

    def add_student(self, name: str) -> Student:
        student = Student(self._students.next_id(), name)
        self._students.save(student)
        return student

    def students(self) -> list[Student]:
        return self._students.all()

    def add_criterion(self, name: str, max_score: float, weight: float) -> Criterion:
        rubric = self._rubrics.get()
        criterion = rubric.add_criterion(name, max_score, weight)
        self._rubrics.save(rubric)
        return criterion

    def criteria(self) -> list[Criterion]:
        return self._rubrics.get().criteria

    def put_evaluation(
        self, student_id: str, criterion_id: str, value: float, comment: str = ""
    ) -> Evaluation:
        student = self._student(student_id)
        evaluation = self._factory.create(self._rubrics.get(), criterion_id, value, comment)
        student.evaluate(evaluation)
        self._students.save(student)
        return evaluation

    def correct_evaluation(
        self, student_id: str, criterion_id: str, value: float, comment: str = ""
    ) -> Evaluation:
        student = self._student(student_id)
        evaluation = self._factory.create(self._rubrics.get(), criterion_id, value, comment)
        student.correct(evaluation)
        self._students.save(student)
        return evaluation

    def cancel_evaluation(self, student_id: str, criterion_id: str) -> None:
        student = self._student(student_id)
        student.cancel(criterion_id.strip())
        self._students.save(student)

    def final_grades(self) -> list[FinalGradeRow]:
        rubric = self._rubrics.get()
        rows = []
        for student in self._students.all():
            grade = self._calculator.final_grade(rubric, student)
            rows.append(FinalGradeRow(student.id, student.name, grade))
        return rows

    @property
    def rule(self) -> FinalGradeRule:
        return self._calculator.rule

    def change_rule(self, rule: FinalGradeRule) -> None:
        self._calculator.change_rule(rule)

    def export_final_grades(self, destination: str) -> int:
        rows = self.final_grades()
        self._exporter.export(rows, destination)
        return len(rows)

    def _student(self, student_id: str) -> Student:
        student = self._students.get(student_id.strip())
        if student is None:
            raise ValueError(f"Студента с номером «{student_id.strip()}» нет")
        return student
