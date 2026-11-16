import pytest

from src.application.facade import PosFacade
from src.domain.evaluation_factory import EvaluationFactory
from src.domain.grading import FinalGradeCalculator, GradedOnlyRule, WeightedSumRule
from src.infrastructure.console_app import ConsoleApp
from src.infrastructure.csv_exporter import CsvGradeExporter
from src.infrastructure.memory_repositories import (
    InMemoryRubricRepository,
    InMemoryStudentRepository,
)


@pytest.fixture
def facade() -> PosFacade:
    return PosFacade(
        InMemoryStudentRepository(),
        InMemoryRubricRepository(),
        EvaluationFactory(),
        FinalGradeCalculator(WeightedSumRule()),
        CsvGradeExporter(),
    )


def run_with_input(monkeypatch, facade: PosFacade, lines: list[str]) -> None:
    answers = iter(lines)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))
    ConsoleApp(facade).run()


def test_menu_scenario(monkeypatch, capsys, facade, tmp_path):
    path = str(tmp_path / "out.csv")
    lines = [
        "1", "Иванов",
        "2", "Лекции", "10", "1",
        "3",
        "4", "1", "1", "6", "",
        "5", "1", "1", "8,5", "пересдал",
        "7",
        "8",
        "10", path,
        "0",
    ]  # fmt: skip
    run_with_input(monkeypatch, facade, lines)

    out = capsys.readouterr().out
    assert "Оценка выставлена" in out
    assert "Оценка исправлена" in out
    assert "8.5 из 10" in out
    assert "«пересдал»" in out
    assert "Иванов: 8.50 из 10" in out
    assert "8.50" in (tmp_path / "out.csv").read_text(encoding="utf-8-sig")


def test_menu_cancel_and_empty_lists(monkeypatch, capsys, facade):
    lines = ["3", "7", "8", "1", "Иванов", "2", "Лекции", "10", "1", "4", "1", "1", "5", "",
             "6", "1", "1", "7", "0"]  # fmt: skip
    run_with_input(monkeypatch, facade, lines)

    out = capsys.readouterr().out
    assert "Пусто." in out
    assert "Студентов нет." in out
    assert "Оценка отменена" in out
    assert "оценок нет" in out


def test_menu_change_rule(monkeypatch, capsys, facade):
    run_with_input(monkeypatch, facade, ["9", "2", "9", "5", "0"])

    out = capsys.readouterr().out
    assert isinstance(facade.rule, GradedOnlyRule)
    assert "Нет такого правила" in out


def test_bad_input_no_crash(monkeypatch, capsys, facade):
    lines = [
        "42",
        "1", "",
        "2", "Лекции", "abc",
        "2", "Лекции", "10", "1",
        "4", "1", "1", "5", "",
        "1", "Иванов",
        "4", "1", "1", "15", "",
        "4", "1", "3", "5", "",
        "6", "1", "1",
        "10", str(__file__) + "/нет/такой/папки.csv",
        "0",
    ]  # fmt: skip
    run_with_input(monkeypatch, facade, lines)

    out = capsys.readouterr().out
    assert "Нет такого пункта" in out
    assert "Имя студента не может быть пустым" in out
    assert "«abc» — не число" in out
    assert "Студента с номером «1» нет" in out
    assert "больше максимума" in out
    assert "нет в рубрикаторе" in out
    assert "оценки нет" in out
    assert out.count("Ошибка:") == 7


def test_exit_on_ctrl_d(monkeypatch, capsys, facade):
    def end_of_input(_prompt=""):
        raise EOFError

    monkeypatch.setattr("builtins.input", end_of_input)
    ConsoleApp(facade).run()

    assert "До свидания" in capsys.readouterr().out


def test_demo(monkeypatch, capsys, facade, tmp_path):
    monkeypatch.chdir(tmp_path)

    run_with_input(monkeypatch, facade, ["11", "11", "0"])

    out = capsys.readouterr().out
    assert "12 из 10: Балл 12 больше максимума" in out
    assert "Критерий 99: Критерия «99» нет в рубрикаторе" in out
    assert "Иванов Иван: 7.57 из 10" in out
    assert "Иванов Иван: 8.83 из 10" in out
    assert "Демо работает только на пустых данных" in out
    assert isinstance(facade.rule, WeightedSumRule)
    assert (tmp_path / "demo_final_grades.csv").exists()


def test_export_default_file(monkeypatch, capsys, facade, tmp_path):
    monkeypatch.chdir(tmp_path)

    run_with_input(monkeypatch, facade, ["10", "", "0"])

    assert (tmp_path / "final_grades.csv").exists()
    assert "записано студентов: 0" in capsys.readouterr().out
