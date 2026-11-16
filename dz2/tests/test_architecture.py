from pathlib import Path

import pytest

from src.application.facade import PosFacade
from src.application.ports import GradeExporter
from src.container import build_container
from src.domain.grading import FinalGradeCalculator, WeightedSumRule
from src.infrastructure.console_app import ConsoleApp
from tests.fakes import FakeExporter

SRC = Path(__file__).parent.parent / "src"


def imports_of(layer: str) -> str:
    text = ""
    for path in (SRC / layer).glob("*.py"):
        text += path.read_text(encoding="utf-8")
    return text


def test_domain_depends_on_nothing_outside():
    text = imports_of("domain")

    assert "src.application" not in text
    assert "src.infrastructure" not in text
    assert "punq" not in text


def test_application_does_not_know_infrastructure():
    text = imports_of("application")

    assert "src.infrastructure" not in text
    assert "punq" not in text


def test_container_builds_app():
    container = build_container()

    assert isinstance(container.resolve(ConsoleApp), ConsoleApp)
    assert container.resolve(PosFacade) is container.resolve(PosFacade)
    assert isinstance(container.resolve(FinalGradeCalculator).rule, WeightedSumRule)


def test_container_fake_exporter():
    container = build_container()
    fake = FakeExporter()
    container.register(GradeExporter, instance=fake)

    facade = container.resolve(PosFacade)
    facade.add_student("Иванов")
    facade.export_final_grades("никуда.csv")

    assert fake.destination == "никуда.csv"
    assert fake.rows[0].name == "Иванов"


@pytest.mark.parametrize("layer", ["domain", "application", "infrastructure"])
def test_layers_are_not_empty(layer):
    assert list((SRC / layer).glob("*.py"))
