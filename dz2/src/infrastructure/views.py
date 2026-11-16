from src.application.ports import FinalGradeRow
from src.domain.grading import MAX_FINAL_GRADE
from src.domain.rubric import Criterion
from src.domain.student import Student
from src.domain.values import Evaluation


def number(value: float) -> str:
    return f"{value:g}"


def student_line(student: Student) -> str:
    return f"  {student.id}. {student.name}"


def criterion_line(criterion: Criterion) -> str:
    return (
        f"  {criterion.id}. {criterion.name} "
        f"(макс {number(criterion.max_score)}, вес {number(criterion.weight)})"
    )


def evaluation_line(evaluation: Evaluation, criterion: Criterion) -> str:
    text = (
        f"     {criterion.name}: {number(evaluation.score.value)} "
        f"из {number(criterion.max_score)}, {evaluation.graded_on:%d.%m.%Y}"
    )
    if evaluation.comment:
        text += f", «{evaluation.comment}»"
    return text


def grade_line(row: FinalGradeRow) -> str:
    return f"  {row.student_id}. {row.name}: {row.grade:.2f} из {MAX_FINAL_GRADE}"
