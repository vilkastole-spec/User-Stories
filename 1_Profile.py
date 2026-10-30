from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime

@dataclass
class User:
    """Пользователь: ФИО и псевдоним."""
    full_name: str
    nickname: str
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def __post_init__(self):
        if not self.full_name.strip():
            raise ValueError("ФИО не может быть пустым")
        if not self.nickname.strip():
            raise ValueError("Псевдоним не может быть пустым")
        if " " in self.nickname:
            raise ValueError("Псевдоним не должен содержать пробелов")

    def __str__(self) -> str:
        return f"[{self.id}] {self.nickname} ({self.full_name})"

@dataclass
class AthleteStats:
    """Физические данные атлета."""
    birth_date: date
    height_cm: float
    weight_kg: float
    gender: str = "не указан"
    experience_years: float = 0.0
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not isinstance(self.birth_date, date):
            raise TypeError("birth_date должен быть date")
        if self.height_cm <= 0:
            raise ValueError("Рост должен быть > 0")
        if self.weight_kg <= 0:
            raise ValueError("Вес должен быть > 0")
        if self.experience_years < 0:
            raise ValueError("Стаж не может быть отрицательным")

    @property
    def age(self) -> int:
        """Полных лет на сегодня."""
        today = date.today()
        years = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            years -= 1
        return years

    @property
    def bmi(self) -> float:
        """Индекс массы тела."""
        h = self.height_cm / 100
        return round(self.weight_kg / (h * h), 2)

    @property
    def bmi_category(self) -> str:
        """Категория ИМТ."""
        b = self.bmi
        if b < 18.5:
            return "недостаточный вес"
        if b < 25:
            return "норма"
        if b < 30:
            return "избыточный вес"
        return "ожирение"

    def update_weight(self, weight_kg: float) -> None:
        """Обновить вес и время последнего изменения."""
        if weight_kg <= 0:
            raise ValueError("Вес должен быть > 0")
        self.weight_kg = weight_kg
        self.updated_at = datetime.now()

@dataclass
class Record:
    """Один личный рекорд."""
    exercise_id: str
    value: float
    unit: str
    achieved_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Значение рекорда должно быть > 0")
        if not self.unit.strip():
            raise ValueError("Нужно указать единицу измерения")

@dataclass
class Records:
    """Личные рекорды атлета."""
    records: dict[str, Record] = field(default_factory=dict)

    def set_record(self, record: Record) -> bool:
        """
        Записать рекорд. Сохраняет только лучший результат по упражнению.
        Возвращает True, если рекорд улучшен (или записан впервые).
        """
        current = self.records.get(record.exercise_id)
        if current is None or record.value > current.value:
            self.records[record.exercise_id] = record
            return True
        return False

    def get(self, exercise_id: str) -> Record | None:
        return self.records.get(exercise_id)

    def remove(self, exercise_id: str) -> None:
        if exercise_id not in self.records:
            raise KeyError(f"Нет рекорда по упражнению id={exercise_id}")
        del self.records[exercise_id]

    def all(self) -> list[Record]:
        return list(self.records.values())

    def best_overall(self) -> Record | None:
        """Самый «большой» рекорд по значению (без учёта единиц)."""
        if not self.records:
            return None
        return max(self.records.values(), key=lambda r: r.value)
