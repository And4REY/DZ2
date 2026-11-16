import pytest

from src.application.facade import PosFacade
from src.application.ports import FinalGradeRow
from src.domain.evaluation_factory import EvaluationFactory
from src.domain.grading import FinalGradeCalculator, GradedOnlyRule, WeightedSumRule
from src.domain.values import Score
from src.infrastructure.memory_repositories import (
    InMemoryRubricRepository,
    InMemoryStudentRepository,
)
from tests.fakes import FakeExporter


@pytest.fixture
def exporter() -> FakeExporter:
    return FakeExporter()


@pytest.fixture
def facade(exporter) -> PosFacade:
    return PosFacade(
        InMemoryStudentRepository(),
        InMemoryRubricRepository(),
        EvaluationFactory(),
        FinalGradeCalculator(WeightedSumRule()),
        exporter,
    )


def test_add_and_list(facade):
    facade.add_student("Иванов")
    facade.add_student("Петрова")
    facade.add_criterion("Лекции", 10, 1)

    assert facade.students()[0].id == "1"
    assert facade.students()[1].id == "2"
    assert facade.criteria()[0].name == "Лекции"


def test_full_scenario(facade, exporter):
    student = facade.add_student("Иванов")
    lectures = facade.add_criterion("Лекции", 10, 1)
    deadlines = facade.add_criterion("Дедлайны", 5, 1)

    facade.put_evaluation(student.id, lectures.id, 6)
    facade.correct_evaluation(student.id, lectures.id, 8, "исправлено")
    facade.put_evaluation(student.id, deadlines.id, 5)
    count = facade.export_final_grades("out.csv")

    assert count == 1
    assert exporter.destination == "out.csv"
    assert exporter.rows == [FinalGradeRow("1", "Иванов", 9.0)]
    assert student.evaluation("1").comment == "исправлено"


def test_cancel_evaluation(facade):
    student = facade.add_student("Иванов")
    facade.add_criterion("Лекции", 10, 1)
    facade.put_evaluation("1", "1", 7)

    facade.cancel_evaluation(" 1 ", " 1 ")

    assert student.evaluations == []


def test_invariants_hold_through_facade(facade):
    student = facade.add_student("Иванов")
    facade.add_criterion("Лекции", 10, 1)

    with pytest.raises(ValueError, match="больше максимума"):
        facade.put_evaluation("1", "1", 12)
    with pytest.raises(ValueError, match="нет в рубрикаторе"):
        facade.put_evaluation("1", "5", 5)
    assert student.evaluations == []


def test_failed_correction_keeps_old_score(facade):
    student = facade.add_student("Иванов")
    facade.add_criterion("Лекции", 10, 1)
    facade.put_evaluation("1", "1", 7)

    with pytest.raises(ValueError):
        facade.correct_evaluation("1", "1", 11)

    assert student.evaluation("1").score == Score(7)


def test_unknown_student(facade):
    facade.add_criterion("Лекции", 10, 1)

    with pytest.raises(ValueError, match="Студента"):
        facade.put_evaluation("7", "1", 5)


def test_change_rule_changes_final_grades(facade):
    facade.add_student("Иванов")
    facade.add_criterion("Лекции", 10, 1)
    facade.add_criterion("Дедлайны", 10, 1)
    facade.put_evaluation("1", "1", 10)
    assert facade.final_grades()[0].grade == 5.0

    facade.change_rule(GradedOnlyRule())

    assert isinstance(facade.rule, GradedOnlyRule)
    assert facade.final_grades()[0].grade == 10.0
