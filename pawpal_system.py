"""PawPal+ logic layer.

Classes: Owner, Pet, Task, Scheduler.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from enum import IntEnum
from typing import Dict, List, Optional


class Priority(IntEnum):
    """Ordered so tasks can be sorted by priority directly (HIGH > MEDIUM > LOW)."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


# Recurrence values a Task accepts. Anything else (including None) is treated
# as a one-off task that does not regenerate when completed.
RECURRENCE_FREQUENCIES = ("daily", "weekly")


@dataclass
class Task:
    """A single pet care activity (e.g. walk, feeding, medication)."""

    title: str
    duration_minutes: int
    priority: Priority
    pet_id: str
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    preferred_time: Optional[time] = None
    completed: bool = False
    recurrence: Optional[str] = None
    due_date: Optional[date] = None

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.completed = False

    def create_next_occurrence(self) -> Optional["Task"]:
        """Build the next occurrence of this task if it recurs.

        Returns a new, incomplete `Task` with the same details and a
        `due_date` moved forward by one day ("daily") or seven days
        ("weekly"). Returns `None` for tasks with no recurrence, since
        those shouldn't regenerate when completed.
        """
        if self.recurrence not in RECURRENCE_FREQUENCIES:
            return None

        base_date = self.due_date or date.today()
        step = timedelta(days=1) if self.recurrence == "daily" else timedelta(days=7)

        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            pet_id=self.pet_id,
            preferred_time=self.preferred_time,
            recurrence=self.recurrence,
            due_date=base_date + step,
        )


@dataclass
class Pet:
    """A pet belonging to an owner, with its own list of care tasks."""

    name: str
    species: str
    owner_id: str
    pet_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    breed: Optional[str] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet, keeping the task's pet_id in sync."""
        task.pet_id = self.pet_id
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a care task from this pet by id."""
        self.tasks = [task for task in self.tasks if task.task_id != task_id]

    def get_tasks(self) -> List[Task]:
        """Return all tasks associated with this pet."""
        return self.tasks

    def mark_task_complete(self, task_id: str) -> Optional[Task]:
        """Mark one of this pet's tasks complete and handle recurrence.

        If the completed task recurs ("daily"/"weekly"), its next occurrence
        is created automatically and added to this pet's task list. Returns
        the newly scheduled follow-up task, or `None` if the task wasn't
        found or doesn't recur.
        """
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        if task is None:
            return None

        task.mark_complete()
        next_task = task.create_next_occurrence()
        if next_task is not None:
            self.add_task(next_task)
        return next_task


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    owner_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    preferences: dict = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's profile, keeping the pet's owner_id in sync."""
        pet.owner_id = self.owner_id
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Remove a pet from this owner's profile by id."""
        self.pets = [pet for pet in self.pets if pet.pet_id != pet_id]

    def get_pets(self) -> List[Pet]:
        """Return all pets belonging to this owner."""
        return self.pets

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Builds and explains a daily care plan from an owner's pets and tasks."""

    def __init__(self, owner: Owner, available_minutes: int = 480) -> None:
        self.owner = owner
        self.available_minutes = available_minutes

    @staticmethod
    def sort_by_time(tasks: List[Task]) -> List[Task]:
        """Return `tasks` sorted by preferred time, earliest first.

        Tasks with no preferred time are sorted to the end rather than
        being treated as "earliest," since they have no actual time slot.
        """
        return sorted(
            tasks,
            key=lambda task: (task.preferred_time is None, task.preferred_time or time.min),
        )

    def filter_tasks(
        self, *, pet_name: Optional[str] = None, completed: Optional[bool] = None
    ) -> List[Task]:
        """Return the owner's tasks narrowed by pet name and/or status.

        Either filter can be left as `None` to skip it; with both omitted,
        every task is returned.
        """
        tasks = self.owner.get_all_tasks()

        if pet_name is not None:
            pet_ids = {pet.pet_id for pet in self.owner.get_pets() if pet.name == pet_name}
            tasks = [task for task in tasks if task.pet_id in pet_ids]

        if completed is not None:
            tasks = [task for task in tasks if task.completed == completed]

        return tasks

    def detect_conflicts(self) -> List[str]:
        """Return warnings for tasks that share the same preferred time.

        This is a lightweight check: it only flags an exact preferred_time
        match, not overlapping durations (e.g. a 30-minute task starting at
        08:00 and a 20-minute task starting at 08:10 won't be flagged even
        though they overlap). Completed tasks and tasks with no preferred
        time are skipped. Returns warning strings instead of raising, so a
        conflict never crashes the program.
        """
        pet_names: Dict[str, str] = {pet.pet_id: pet.name for pet in self.owner.get_pets()}

        tasks_by_time: Dict[time, List[Task]] = {}
        for task in self.owner.get_all_tasks():
            if task.completed or task.preferred_time is None:
                continue
            tasks_by_time.setdefault(task.preferred_time, []).append(task)

        warnings: List[str] = []
        for scheduled_time, tasks in sorted(tasks_by_time.items()):
            if len(tasks) < 2:
                continue
            names = ", ".join(
                f"{task.title} ({pet_names.get(task.pet_id, 'Unknown pet')})" for task in tasks
            )
            warnings.append(f"Conflict at {scheduled_time.strftime('%H:%M')}: {names}")

        return warnings

    def build_schedule(self) -> List[Task]:
        """Choose and order tasks into a daily plan based on priority, preferred
        time, and the available time budget.

        Reads tasks via `Owner.get_all_tasks()` so every pet is considered, not
        just one. Completed tasks are skipped. Remaining tasks are sorted by
        priority (high first), then by preferred time (earliest first, with
        tasks that have no preferred time sorted last). Tasks are then added
        greedily until the time budget runs out.
        """
        candidates = [task for task in self.owner.get_all_tasks() if not task.completed]
        candidates.sort(
            key=lambda task: (
                -task.priority,
                task.preferred_time is None,
                task.preferred_time or time.min,
            )
        )

        schedule: List[Task] = []
        remaining_minutes = self.available_minutes
        for task in candidates:
            if task.duration_minutes <= remaining_minutes:
                schedule.append(task)
                remaining_minutes -= task.duration_minutes

        return schedule

    def explain_plan(self, schedule: List[Task]) -> str:
        """Return a human-readable explanation of why/when each task was chosen."""
        if not schedule:
            return "No tasks were scheduled."

        pet_names: Dict[str, str] = {pet.pet_id: pet.name for pet in self.owner.pets}

        lines = ["Today's Schedule:"]
        total_minutes = 0
        for task in schedule:
            total_minutes += task.duration_minutes
            time_label = task.preferred_time.strftime("%H:%M") if task.preferred_time else "Anytime"
            pet_name = pet_names.get(task.pet_id, "Unknown pet")
            lines.append(
                f"  {time_label} | {task.title} ({task.duration_minutes} min) "
                f"[priority: {task.priority.name}] - for {pet_name}"
            )
        lines.append(
            f"Total: {total_minutes}/{self.available_minutes} minutes used"
        )
        return "\n".join(lines)
