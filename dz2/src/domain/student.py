from src.domain.values import Evaluation


class Student:
    def __init__(self, student_id: str, name: str) -> None:
        if not name.strip():
            raise ValueError("Имя студента не может быть пустым")
        self._id = student_id
        self._name = name.strip()
        self._evaluations: dict[str, Evaluation] = {}

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def evaluations(self) -> list[Evaluation]:
        return list(self._evaluations.values())

    def evaluation(self, criterion_id: str) -> Evaluation | None:
        return self._evaluations.get(criterion_id)

    def evaluate(self, evaluation: Evaluation) -> None:
        if evaluation.criterion_id in self._evaluations:
            raise ValueError("По этому критерию оценка уже есть, её можно исправить")
        self._evaluations[evaluation.criterion_id] = evaluation

    def correct(self, evaluation: Evaluation) -> None:
        self._require(evaluation.criterion_id)
        self._evaluations[evaluation.criterion_id] = evaluation

    def cancel(self, criterion_id: str) -> None:
        self._require(criterion_id)
        del self._evaluations[criterion_id]

    def _require(self, criterion_id: str) -> None:
        if criterion_id not in self._evaluations:
            raise ValueError("По этому критерию оценки нет")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Student) and other.id == self.id

    def __hash__(self) -> int:
        return hash(self._id)
