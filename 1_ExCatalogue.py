import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
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

@dataclass
class Training:
    starts_at: datetime
    duration: timedelta = timedelta(hours=1)
    exercise_ids: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.starts_at, datetime):
            raise TypeError("starts_at должен быть datetime")
        if self.duration <= timedelta(0):
            raise ValueError("Длительность должна быть > 0")

    @property
    def ends_at(self) -> datetime:
        return self.starts_at + self.duration

    def add_exercise(self, exercise: Exercise | str) -> None:
        ex_id = exercise.id if isinstance(exercise, Exercise) else exercise
        if ex_id in self.exercise_ids:
            raise ValueError(f"id={ex_id} уже в тренировке")
        self.exercise_ids.append(ex_id)

    def remove_exercise(self, exercise_id: str) -> None:
        if exercise_id not in self.exercise_ids:
            raise KeyError(f"id={exercise_id} нет в тренировке")
        self.exercise_ids.remove(exercise_id)
