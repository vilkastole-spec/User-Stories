import uuid
from dataclasses import dataclass, field
from enum import Enum

class ExerciseKind(str, Enum):
    STRENGTH = "силовое"
    SPEED = "скоростное"
    ENDURANCE = "выносливость"
    FLEXIBILITY = "гибкость"
    COORDINATION = "координация"
    BALANCE = "баланс"
    CARDIO = "кардио"

class MuscleGroup(str, Enum):
    CHEST = "грудь"
    BACK = "спина"
    SHOULDERS = "плечи"
    BICEPS = "бицепс"
    TRICEPS = "трицепс"
    ABS = "пресс"
    GLUTES = "ягодицы"
    QUADRICEPS = "квадрицепс"
    HAMSTRINGS = "бицепс бедра"
    CALVES = "икры"
    FOREARMS = "предплечья"
    FULL_BODY = "всё тело"

@dataclass
class Exercise:
    """Упражнение: вид, группы мышц, название, описание, id."""
    name: str
    kind: ExerciseKind
    muscle_groups: set[MuscleGroup]
    description: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Название не может быть пустым")
        if not self.muscle_groups:
            raise ValueError("Укажи хотя бы одну группу мышц")
        if isinstance(self.kind, str):
            self.kind = ExerciseKind(self.kind.lower())

    def __str__(self) -> str:
        groups = ", ".join(g.value for g in self.muscle_groups)
        return f"[{self.id}] {self.name} ({self.kind.value}; {groups})"

class ExerciseCatalog:

    def __init__(self) -> None:
        self._items: dict[str, Exercise] = {}

    def add(self, exercise: Exercise) -> Exercise:
        if exercise.id in self._items:
            raise ValueError(f"id={exercise.id} уже занят")
        self._items[exercise.id] = exercise
        return exercise

    def get(self, exercise_id: str) -> Exercise:
        if exercise_id not in self._items:
            raise KeyError(f"Нет упражнения id={exercise_id}")
        return self._items[exercise_id]

    def all(self) -> list[Exercise]:
        return list(self._items.values())

    def by_kind(self, kind: ExerciseKind) -> list[Exercise]:
        return [ex for ex in self._items.values() if ex.kind == kind]

    def by_muscle_group(self, group: MuscleGroup) -> list[Exercise]:
        return [ex for ex in self._items.values() if group in ex.muscle_groups]

    def search(self, query: str) -> list[Exercise]:
        q = query.lower().strip()
        return [
            ex for ex in self._items.values()
            if q in ex.name.lower() or q in ex.description.lower()
        ]
