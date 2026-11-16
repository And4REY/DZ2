from src.application.facade import PosFacade
from src.domain.grading import FinalGradeRule, GradedOnlyRule, WeightedSumRule
from src.infrastructure.demo import run_demo
from src.infrastructure.views import criterion_line, evaluation_line, grade_line, student_line

RULES: dict[str, FinalGradeRule] = {
    "1": WeightedSumRule(),
    "2": GradedOnlyRule(),
}
DEFAULT_FILE = "final_grades.csv"


def ask_float(prompt: str) -> float:
    text = input(prompt).strip().replace(",", ".")
    try:
        return float(text)
    except ValueError:
        raise ValueError(f"«{text}» — не число") from None


class ConsoleApp:
    def __init__(self, facade: PosFacade) -> None:
        self._facade = facade
        self._actions = {
            "1": self.add_student,
            "2": self.add_criterion,
            "3": self.show_lists,
            "4": self.put_evaluation,
            "5": self.correct_evaluation,
            "6": self.cancel_evaluation,
            "7": self.show_evaluations,
            "8": self.show_final_grades,
            "9": self.change_rule,
            "10": self.export,
            "11": self.demo,
        }

    def run(self) -> None:
        print("ПОС: преподавательская оценка студентов")
        while True:
            self._print_menu()
            try:
                choice = input("> ").strip()
                if choice == "0":
                    print("До свидания!")
                    return
                action = self._actions.get(choice)
                if action is None:
                    print("Нет такого пункта.")
                    continue
                action()
            except (ValueError, OSError) as error:
                print(f"Ошибка: {error}")
            except (EOFError, KeyboardInterrupt):
                print("\nДо свидания!")
                return

    @staticmethod
    def _print_menu() -> None:
        print()
        print("1. Добавить студента")
        print("2. Добавить критерий")
        print("3. Студенты и критерии")
        print("4. Выставить оценку")
        print("5. Исправить оценку")
        print("6. Отменить оценку")
        print("7. Все оценки")
        print("8. Итоги")
        print("9. Правило итога")
        print("10. Экспорт итогов в CSV")
        print("11. Демо")
        print("0. Выход")

    def add_student(self) -> None:
        student = self._facade.add_student(input("Имя студента: "))
        print(f"Добавлен студент {student.id}. {student.name}")

    def add_criterion(self) -> None:
        name = input("Название критерия: ")
        max_score = ask_float("Максимальный балл: ")
        weight = ask_float("Вес: ")
        criterion = self._facade.add_criterion(name, max_score, weight)
        print(f"Добавлен критерий {criterion.id}. {criterion.name}")

    def show_lists(self) -> None:
        print("Студенты")
        students = self._facade.students()
        if not students:
            print("  Пусто.")
        for student in students:
            print(student_line(student))
        print("Критерии")
        criteria = self._facade.criteria()
        if not criteria:
            print("  Пусто.")
        for criterion in criteria:
            print(criterion_line(criterion))

    def put_evaluation(self) -> None:
        student_id = input("Номер студента: ")
        criterion_id = input("Номер критерия: ")
        value = ask_float("Балл: ")
        comment = input("Комментарий (Enter, если не нужен): ")
        self._facade.put_evaluation(student_id, criterion_id, value, comment)
        print("Оценка выставлена.")

    def correct_evaluation(self) -> None:
        student_id = input("Номер студента: ")
        criterion_id = input("Номер критерия: ")
        value = ask_float("Новый балл: ")
        comment = input("Комментарий (Enter, если не нужен): ")
        self._facade.correct_evaluation(student_id, criterion_id, value, comment)
        print("Оценка исправлена.")

    def cancel_evaluation(self) -> None:
        student_id = input("Номер студента: ")
        criterion_id = input("Номер критерия: ")
        self._facade.cancel_evaluation(student_id, criterion_id)
        print("Оценка отменена.")

    def show_evaluations(self) -> None:
        students = self._facade.students()
        if not students:
            print("Студентов нет.")
        criteria = {}
        for criterion in self._facade.criteria():
            criteria[criterion.id] = criterion
        for student in students:
            print(student_line(student))
            if not student.evaluations:
                print("     оценок нет")
            for evaluation in student.evaluations:
                print(evaluation_line(evaluation, criteria[evaluation.criterion_id]))

    def show_final_grades(self) -> None:
        print(f"Итоги, правило: {self._facade.rule.title}")
        rows = self._facade.final_grades()
        if not rows:
            print("  Студентов нет.")
        for row in rows:
            print(grade_line(row))

    def change_rule(self) -> None:
        print(f"Сейчас: {self._facade.rule.title}")
        for key in RULES:
            print(f"  {key}. {RULES[key].title}")
        choice = input("> ").strip()
        if choice not in RULES:
            raise ValueError("Нет такого правила")
        self._facade.change_rule(RULES[choice])
        print(f"Теперь итог считается {RULES[choice].title}.")

    def export(self) -> None:
        destination = input(f"Файл (Enter = {DEFAULT_FILE}): ").strip()
        if not destination:
            destination = DEFAULT_FILE
        count = self._facade.export_final_grades(destination)
        print(f"В файл {destination} записано студентов: {count}")

    def demo(self) -> None:
        if self._facade.students() or self._facade.criteria():
            print("Демо работает только на пустых данных. Перезапустите программу.")
            return
        run_demo(self._facade)
