from abc import ABC, abstractmethod

from src.domain.rubric import Rubric
from src.domain.student import Student

MAX_FINAL_GRADE = 10


class FinalGradeRule(ABC):
    title = ""

    @abstractmethod
    def calculate(self, rubric: Rubric, student: Student) -> float:
        pass


class WeightedSumRule(FinalGradeRule):
    title = "по всем критериям (нет оценки = 0)"

    def calculate(self, rubric: Rubric, student: Student) -> float:
        total = 0.0
        weights = 0.0
        for criterion in rubric.criteria:
            weights += criterion.weight
            evaluation = student.evaluation(criterion.id)
            if evaluation is not None:
                total += criterion.share(evaluation.score) * criterion.weight
        if weights == 0:
            return 0.0
        return total / weights * MAX_FINAL_GRADE


class GradedOnlyRule(FinalGradeRule):
    title = "только по выставленным оценкам"

    def calculate(self, rubric: Rubric, student: Student) -> float:
        total = 0.0
        weights = 0.0
        for criterion in rubric.criteria:
            evaluation = student.evaluation(criterion.id)
            if evaluation is not None:
                weights += criterion.weight
                total += criterion.share(evaluation.score) * criterion.weight
        if weights == 0:
            return 0.0
        return total / weights * MAX_FINAL_GRADE


class FinalGradeCalculator:
    def __init__(self, rule: FinalGradeRule) -> None:
        self._rule = rule

    @property
    def rule(self) -> FinalGradeRule:
        return self._rule

    def change_rule(self, rule: FinalGradeRule) -> None:
        self._rule = rule

    def final_grade(self, rubric: Rubric, student: Student) -> float:
        for evaluation in student.evaluations:
            if not rubric.contains(evaluation.criterion_id):
                raise ValueError(
                    f"У студента {student.name} оценка по критерию "
                    f"«{evaluation.criterion_id}», которого нет в рубрикаторе"
                )
        return round(self._rule.calculate(rubric, student), 2)
