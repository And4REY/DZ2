from datetime import date

import pytest

from src.domain.evaluation_factory import EvaluationFactory
from src.domain.grading import FinalGradeCalculator, GradedOnlyRule, WeightedSumRule
from src.domain.rubric import Rubric
from src.domain.student import Student
from src.domain.values import Evaluation, Score


@pytest.fixture
def rubric() -> Rubric:
    rubric = Rubric()
    rubric.add_criterion("Лекции", 10, 1)
    rubric.add_criterion("Дедлайны", 10, 3)
    return rubric


@pytest.fixture
def student(rubric) -> Student:
    student = Student("1", "Иванов")
    student.evaluate(EvaluationFactory().create(rubric, "1", 8))
    return student


def test_weighted_sum_counts_missing_as_zero(rubric, student):
    assert WeightedSumRule().calculate(rubric, student) == pytest.approx(2.0)


def test_graded_only_skips_missing(rubric, student):
    assert GradedOnlyRule().calculate(rubric, student) == pytest.approx(8.0)


def test_all_criteria_graded_rules_agree(rubric, student):
    student.evaluate(EvaluationFactory().create(rubric, "2", 6))

    assert WeightedSumRule().calculate(rubric, student) == pytest.approx(6.5)
    assert GradedOnlyRule().calculate(rubric, student) == pytest.approx(6.5)


def test_full_marks_give_ten(rubric):
    student = Student("1", "Иванов")
    student.evaluate(EvaluationFactory().create(rubric, "1", 10))
    student.evaluate(EvaluationFactory().create(rubric, "2", 10))

    assert FinalGradeCalculator(WeightedSumRule()).final_grade(rubric, student) == 10


def test_empty_data_gives_zero(rubric):
    empty_student = Student("2", "Петров")

    assert WeightedSumRule().calculate(Rubric(), empty_student) == 0
    assert GradedOnlyRule().calculate(rubric, empty_student) == 0


def test_calculator_rounds(rubric):
    student = Student("1", "Иванов")
    student.evaluate(EvaluationFactory().create(rubric, "1", 1))

    assert FinalGradeCalculator(WeightedSumRule()).final_grade(rubric, student) == 0.25


def test_calculator_follows_current_evaluations(rubric, student):
    calculator = FinalGradeCalculator(WeightedSumRule())
    assert calculator.final_grade(rubric, student) == 2.0

    student.correct(EvaluationFactory().create(rubric, "1", 4))
    assert calculator.final_grade(rubric, student) == 1.0

    student.cancel("1")
    assert calculator.final_grade(rubric, student) == 0


def test_calculator_change_rule(rubric, student):
    calculator = FinalGradeCalculator(WeightedSumRule())

    calculator.change_rule(GradedOnlyRule())

    assert isinstance(calculator.rule, GradedOnlyRule)
    assert calculator.final_grade(rubric, student) == 8.0


def test_calculator_rejects_evaluation_outside_rubric(rubric):
    student = Student("1", "Иванов")
    student.evaluate(Evaluation("99", Score(5), date.today()))

    with pytest.raises(ValueError, match="нет в рубрикаторе"):
        FinalGradeCalculator(WeightedSumRule()).final_grade(rubric, student)
