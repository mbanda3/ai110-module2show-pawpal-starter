"""Quick tests for the PawPal+ logic layer."""

from pawpal_system import Pet, Priority, Task


def test_mark_complete_changes_task_status():
    task = Task(title="Feeding", duration_minutes=10, priority=Priority.HIGH, pet_id="pet-1")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", owner_id="owner-1")
    task = Task(title="Walk", duration_minutes=20, priority=Priority.MEDIUM, pet_id=pet.pet_id)
    assert len(pet.get_tasks()) == 0

    pet.add_task(task)

    assert len(pet.get_tasks()) == 1
