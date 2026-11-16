import math

from src.domain.values import Score


class Criterion:
    def __init__(self, criterion_id: str, name: str, max_score: float, weight: float) -> None:
        if not name.strip():
            raise ValueError("Название критерия не может быть пустым")
        if not math.isfinite(max_score) or max_score <= 0:
            raise ValueError("Максимальный балл должен быть больше 0")
        if not math.isfinite(weight) or weight <= 0:
            raise ValueError("Вес должен быть больше 0")
        self._id = criterion_id
        self._name = name.strip()
        self._max_score = max_score
        self._weight = weight

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def max_score(self) -> float:
        return self._max_score

    @property
    def weight(self) -> float:
        return self._weight

    def check(self, score: Score) -> None:
        if score.value > self._max_score:
            raise ValueError(
                f"Балл {score.value:g} больше максимума {self._max_score:g} "
                f"по критерию «{self._name}»"
            )

    def share(self, score: Score) -> float:
        return score.value / self._max_score

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Criterion) and other.id == self.id

    def __hash__(self) -> int:
        return hash(self._id)


class Rubric:
    def __init__(self) -> None:
        self._criteria: dict[str, Criterion] = {}

    @property
    def criteria(self) -> list[Criterion]:
        return list(self._criteria.values())

    def add_criterion(self, name: str, max_score: float, weight: float) -> Criterion:
        for criterion in self._criteria.values():
            if criterion.name.lower() == name.strip().lower():
                raise ValueError(f"Критерий «{criterion.name}» уже есть в рубрикаторе")
        criterion = Criterion(str(len(self._criteria) + 1), name, max_score, weight)
        self._criteria[criterion.id] = criterion
        return criterion

    def contains(self, criterion_id: str) -> bool:
        return criterion_id in self._criteria

    def criterion(self, criterion_id: str) -> Criterion:
        if not self.contains(criterion_id):
            raise ValueError(f"Критерия «{criterion_id}» нет в рубрикаторе")
        return self._criteria[criterion_id]
