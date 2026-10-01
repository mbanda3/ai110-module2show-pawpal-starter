"""PawPal+ logic layer skeleton.

Classes: Owner, Pet, Task, Scheduler.
This is a skeleton generated from diagrams/uml.mmd — attributes and method
signatures only. Method bodies are stubs and are implemented in later phases.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time
from enum import Enum
from typing import List, Optional


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    pet_id: str
    task_id: Optional[str] = None
    preferred_time: Optional[time] = None
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        raise NotImplementedError

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        raise NotImplementedError


@dataclass
class Pet:
    name: str
    species: str
    owner_id: str
    pet_id: Optional[str] = None
    breed: Optional[str] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        raise NotImplementedError

    def remove_task(self, task_id: str) -> None:
        """Remove a care task from this pet by id."""
        raise NotImplementedError

    def get_tasks(self) -> List[Task]:
        """Return all tasks associated with this pet."""
        raise NotImplementedError


@dataclass
class Owner:
    name: str
    owner_id: Optional[str] = None
    preferences: dict = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's profile."""
        raise NotImplementedError

    def remove_pet(self, pet_id: str) -> None:
        """Remove a pet from this owner's profile by id."""
        raise NotImplementedError

    def get_pets(self) -> List[Pet]:
        """Return all pets belonging to this owner."""
        raise NotImplementedError


class Scheduler:
    """Builds and explains a daily care plan from an owner's pets and tasks."""

    def __init__(self, owner: Owner, available_minutes: int = 480) -> None:
        self.owner = owner
        self.available_minutes = available_minutes

    def build_schedule(self) -> List[Task]:
        """Choose and order tasks into a daily plan based on constraints."""
        raise NotImplementedError

    def explain_plan(self, schedule: List[Task]) -> str:
        """Return a human-readable explanation of why/when each task was chosen."""
        raise NotImplementedError
