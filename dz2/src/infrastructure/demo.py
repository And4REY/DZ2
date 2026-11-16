from src.application.facade import PosFacade
from src.domain.grading import GradedOnlyRule
from src.infrastructure.views import criterion_line, grade_line, student_line

DEMO_FILE = "demo_final_grades.csv"


def run_demo(facade: PosFacade, destination: str = DEMO_FILE) -> None:
    print("Демо: студенты, критерии, оценки, итог, экспорт")

    print()
    print("1. Заводим студентов")
    ivanov = facade.add_student("Иванов Иван")
    petrova = facade.add_student("Петрова Анна")
    sidorov = facade.add_student("Сидоров Пётр")
    for student in facade.students():
        print(student_line(student))

    print()
    print("2. Заводим критерии")
    lectures = facade.add_criterion("Посещал лекции", 10, 1)
    deadlines = facade.add_criterion("Не нарушал дедлайны", 10, 2)
    seminars = facade.add_criterion("Ходил на семинары", 5, 1)
    ai = facade.add_criterion("ИИ использовал, но понял сам", 10, 3)
    for criterion in facade.criteria():
        print(criterion_line(criterion))

    print()
    print("3. Выставляем оценки")
    grades = [
        (ivanov, lectures, 9),
        (ivanov, deadlines, 10),
        (ivanov, seminars, 4),
        (ivanov, ai, 8),
        (petrova, lectures, 10),
        (petrova, deadlines, 6),
        (petrova, seminars, 5),
        (petrova, ai, 10),
        (sidorov, lectures, 6),
        (sidorov, ai, 9),
    ]
    for student, criterion, value in grades:
        facade.put_evaluation(student.id, criterion.id, value)
        print(f"  {student.name}, {criterion.name}: {value}")

    print()
    print("4. Пробуем нарушить правила")
    try:
        facade.put_evaluation(sidorov.id, deadlines.id, 12)
    except ValueError as error:
        print(f"  12 из 10: {error}")
    try:
        facade.put_evaluation(sidorov.id, "99", 5)
    except ValueError as error:
        print(f"  Критерий 99: {error}")
    try:
        facade.put_evaluation(ivanov.id, lectures.id, 5)
    except ValueError as error:
        print(f"  Вторая оценка: {error}")

    print()
    print("5. Исправляем и отменяем")
    facade.correct_evaluation(petrova.id, deadlines.id, 9, "опоздание по уважительной причине")
    print(f"  {petrova.name}, {deadlines.name}: исправлено на 9")
    facade.cancel_evaluation(ivanov.id, seminars.id)
    print(f"  {ivanov.name}, {seminars.name}: оценка отменена")

    print()
    print(f"6. Итог, правило: {facade.rule.title}")
    for row in facade.final_grades():
        print(grade_line(row))
    previous_rule = facade.rule
    facade.change_rule(GradedOnlyRule())
    print(f"   Итог, правило: {facade.rule.title}")
    for row in facade.final_grades():
        print(grade_line(row))
    facade.change_rule(previous_rule)

    print()
    print("7. Экспорт итога")
    count = facade.export_final_grades(destination)
    print(f"  В файл {destination} записано студентов: {count}")
