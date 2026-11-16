from datetime import date

from src.domain.rubric import Rubric
from src.domain.values import Evaluation, Score


class EvaluationFactory:
    def create(
        self, rubric: Rubric, criterion_id: str, value: float, comment: str = ""
    ) -> Evaluation:
        criterion = rubric.criterion(criterion_id.strip())
        score = Score(value)
        criterion.check(score)
        return Evaluation(criterion.id, score, date.today(), comment.strip())
