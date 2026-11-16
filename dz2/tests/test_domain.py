from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from src.domain.evaluation_factory import EvaluationFactory
from src.domain.rubric import Criterion, Rubric
from src.domain.student import Student
from src.domain.values import Evaluation, Score


@pytest.fixture
def rubric() -> Rubric:
    rubric = Rubric()
    rubric.add_criterion("Лекции", 10, 1)
    rubric.add_criterion("Семинары", 5, 2)
    return rubric


def test_score_equal_by_value():
    assert Score(7) == Score(7)
    assert Score(7) != Score(8)


def test_score_cannot_change():
    score = Score(7)

    with pytest.raises(FrozenInstanceError):
        score.value = 8


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf")])
def test_bad_score(value):
    with pytest.raises(ValueError):
        Score(value)


@pytest.mark.parametrize(
    "name, max_score, weight",
    [("", 10, 1), ("Лекции", 0, 1), ("Лекции", 10, 0), ("Лекции", 10, -2)],
)
def test_bad_criterion(name, max_score, weight):
    with pytest.raises(ValueError):
        Criterion("1", name, max_score, weight)


def test_criterion_check_boundary():
    criterion = Criterion("1", "Лекции", 10, 1)

    criterion.check(Score(10))
    with pytest.raises(ValueError, match="больше максимума"):
        criterion.check(Score(10.5))


def test_criterion_share():
    assert Criterion("1", "Лекции", 10, 1).share(Score(5)) == 0.5


def test_rubric_gives_ids(rubric):
    assert rubric.criteria[0].id == "1"
    assert rubric.criteria[1].id == "2"
    assert rubric.criterion("2").name == "Семинары"


def test_rubric_no_duplicate_names(rubric):
    with pytest.raises(ValueError, match="уже есть"):
        rubric.add_criterion(" лекции ", 5, 1)


def test_rubric_unknown_criterion(rubric):
    assert not rubric.contains("99")
    with pytest.raises(ValueError, match="нет в рубрикаторе"):
        rubric.criterion("99")


def test_entities_equal_by_id():
    assert Student("1", "Иванов") == Student("1", "Иванов Иван")
    assert Student("1", "Иванов") != Student("2", "Иванов")
    assert Criterion("1", "Лекции", 10, 1) == Criterion("1", "Другое", 5, 2)
    assert len({Student("1", "А"), Student("1", "Б")}) == 1
    assert len({Criterion("1", "А", 5, 1), Criterion("1", "Б", 9, 2)}) == 1


def test_student_empty_name():
    with pytest.raises(ValueError):
        Student("1", "   ")


def test_factory_creates_evaluation(rubric):
    evaluation = EvaluationFactory().create(rubric, " 1 ", 8, " молодец ")

    assert evaluation == Evaluation("1", Score(8), date.today(), "молодец")


def test_factory_max_score_is_allowed(rubric):
    assert EvaluationFactory().create(rubric, "2", 5).score == Score(5)


def test_factory_rejects_score_above_max(rubric):
    with pytest.raises(ValueError, match="больше максимума"):
        EvaluationFactory().create(rubric, "1", 12)


def test_factory_rejects_negative_score(rubric):
    with pytest.raises(ValueError, match="отрицательным"):
        EvaluationFactory().create(rubric, "1", -1)


def test_factory_rejects_unknown_criterion(rubric):
    with pytest.raises(ValueError, match="нет в рубрикаторе"):
        EvaluationFactory().create(rubric, "99", 5)


def test_student_evaluate_correct_cancel(rubric):
    factory = EvaluationFactory()
    student = Student("1", "Иванов")

    student.evaluate(factory.create(rubric, "1", 6))
    student.correct(factory.create(rubric, "1", 9))
    assert student.evaluation("1").score == Score(9)

    student.cancel("1")
    assert student.evaluation("1") is None
    assert student.evaluations == []


def test_student_second_evaluation_forbidden(rubric):
    factory = EvaluationFactory()
    student = Student("1", "Иванов")
    student.evaluate(factory.create(rubric, "1", 6))

    with pytest.raises(ValueError, match="уже есть"):
        student.evaluate(factory.create(rubric, "1", 7))


def test_student_correct_or_cancel_missing(rubric):
    student = Student("1", "Иванов")

    with pytest.raises(ValueError, match="оценки нет"):
        student.correct(EvaluationFactory().create(rubric, "1", 6))
    with pytest.raises(ValueError, match="оценки нет"):
        student.cancel("1")
