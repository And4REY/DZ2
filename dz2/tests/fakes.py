from src.application.ports import FinalGradeRow, GradeExporter


class FakeExporter(GradeExporter):
    def __init__(self) -> None:
        self.rows: list[FinalGradeRow] = []
        self.destination = ""

    def export(self, rows: list[FinalGradeRow], destination: str) -> None:
        self.rows = rows
        self.destination = destination
