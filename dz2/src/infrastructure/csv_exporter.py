import csv

from src.application.ports import FinalGradeRow, GradeExporter


class CsvGradeExporter(GradeExporter):
    def export(self, rows: list[FinalGradeRow], destination: str) -> None:
        with open(destination, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(["Номер", "Студент", "Итог"])
            for row in rows:
                writer.writerow([row.student_id, row.name, f"{row.grade:.2f}"])
