from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from training import ExerciseCatalog, ExerciseKind

@dataclass
class Restrictions:
    min_duration: timedelta | None = None
    max_duration: timedelta | None = None
    max_strength_ratio: float | None = None
    max_exercises: int | None = None

    def __post_init__(self):
        if self.min_duration and self.min_duration <= timedelta(0):
            raise ValueError("длительность должна быть > 0")
        if self.max_duration and self.max_duration <= timedelta(0):
            raise ValueError("длительность должна быть > 0")
        if self.min_duration and self.max_duration and self.min_duration > self.max_duration:
            raise ValueError("минимальная длительность не может быть больше максимальной")
        if self.max_strength_ratio is not None and not 0.0 <= self.max_strength_ratio <= 1.0:
            raise ValueError("доля силовых подходов должна быть в [0.0, 1.0]")
        if self.max_exercises is not None and self.max_exercises < 1:
            raise ValueError("Количество упражнений должено быть >= 1")

@dataclass
class Set:
    exercise_id: str
    starts_at: datetime
    duration: timedelta = timedelta(minutes=10)

    def __post_init__(self):
        if not isinstance(self.starts_at, datetime):
            raise TypeError("не datetime")
        if self.duration <= timedelta(0):
            raise ValueError("Длительность подхода должна быть > 0")

    @property
    def ends_at(self) -> datetime:
        return self.starts_at + self.duration

class Session:
  
    description: str
    repeats: int = 1
    sets: list[Set] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    MIN_SETS = 3
    MAX_SETS = 4

    def __post_init__(self):
        if self.repeats < 1:
            raise ValueError("repeats должен быть >= 1")

    def add_set(self, set_: Set) -> None:
        if len(self.sets) >= self.MAX_SETS:
            raise ValueError(f"В сессии не может быть больше {self.MAX_SETS} подходов")
        self.sets.append(set_)

    def remove_set(self, set_index: int) -> None:
        if not 0 <= set_index < len(self.sets):
            raise IndexError(set_index)
        del self.sets[set_index]

    @property
    def exercise_ids(self) -> list[str]:
        return [s.exercise_id for s in self.sets]

    @property
    def schedule(self) -> list[tuple[str, datetime, datetime]]:
        return [(s.exercise_id, s.starts_at, s.ends_at) for s in self.sets]

    @property
    def date(self) -> date | None:
        if not self.sets:
            return None
        return min(s.starts_at for s in self.sets).date()

    @property
    def total_duration(self) -> timedelta:
        total = sum((s.duration for s in self.sets), timedelta())
        return total * self.repeats

    def validate(self, catalog: ExerciseCatalog, restrictions: Restrictions) -> list[str]:
        errors: list[str] = []

        if len(self.sets) < self.MIN_SETS:
            errors.append(
                f"Нужно минимум {self.MIN_SETS} подхода в сессии, есть {len(self.sets)}"
            )

        total = self.total_duration
        if restrictions.min_duration and total < restrictions.min_duration:
            errors.append(f"Сессия короче минимума: {total} < {restrictions.min_duration}")
        if restrictions.max_duration and total > restrictions.max_duration:
            errors.append(f"Сессия длиннее максимума: {total} > {restrictions.max_duration}")

        if restrictions.max_exercises is not None and len(self.sets) > restrictions.max_exercises:
            errors.append(
                f"Подходов {len(self.sets)} больше максимума {restrictions.max_exercises}"
            )

        if restrictions.max_strength_ratio is not None and self.sets:
            strength = 0
            for s in self.sets:
                ex = catalog.get(s.exercise_id)
                if ex.kind == ExerciseKind.STRENGTH:
                    strength += 1
            ratio = strength / len(self.sets)
            if ratio > restrictions.max_strength_ratio:
                errors.append(
                    f"Доля силовых {ratio:.2f} превышает {restrictions.max_strength_ratio:.2f}"
                )

        return errors
