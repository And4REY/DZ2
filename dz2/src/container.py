import punq

from src.application.facade import PosFacade
from src.application.ports import GradeExporter
from src.domain.evaluation_factory import EvaluationFactory
from src.domain.grading import FinalGradeCalculator, FinalGradeRule, WeightedSumRule
from src.domain.repositories import RubricRepository, StudentRepository
from src.infrastructure.console_app import ConsoleApp
from src.infrastructure.csv_exporter import CsvGradeExporter
from src.infrastructure.memory_repositories import (
    InMemoryRubricRepository,
    InMemoryStudentRepository,
)


def build_container() -> punq.Container:
    container = punq.Container()
    container.register(StudentRepository, InMemoryStudentRepository, scope=punq.Scope.singleton)
    container.register(RubricRepository, InMemoryRubricRepository, scope=punq.Scope.singleton)
    container.register(EvaluationFactory)
    container.register(FinalGradeRule, WeightedSumRule)
    container.register(FinalGradeCalculator, scope=punq.Scope.singleton)
    container.register(GradeExporter, CsvGradeExporter)
    container.register(PosFacade, scope=punq.Scope.singleton)
    container.register(ConsoleApp)
    return container
