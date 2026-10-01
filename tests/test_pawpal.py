"""Quick tests for the PawPal+ logic layer."""

from datetime import date, time, timedelta

from pawpal_system import Owner, Pet, Priority, Scheduler, Task


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


def test_sort_by_time_orders_tasks_and_puts_no_time_last():
    pet = Pet(name="Mochi", species="dog", owner_id="owner-1")
    evening = Task(title="Evening walk", duration_minutes=20, priority=Priority.LOW, pet_id=pet.pet_id, preferred_time=time(18, 0))
    anytime = Task(title="Brushing", duration_minutes=5, priority=Priority.LOW, pet_id=pet.pet_id)
    morning = Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH, pet_id=pet.pet_id, preferred_time=time(8, 0))

    ordered = Scheduler.sort_by_time([evening, anytime, morning])

    assert [task.title for task in ordered] == ["Morning walk", "Evening walk", "Brushing"]


def test_filter_tasks_by_pet_name_and_completion_status():
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog", owner_id=owner.owner_id)
    luna = Pet(name="Luna", species="cat", owner_id=owner.owner_id)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    walk = Task(title="Walk", duration_minutes=20, priority=Priority.MEDIUM, pet_id=mochi.pet_id)
    walk.mark_complete()
    mochi.add_task(walk)
    feeding = Task(title="Feeding", duration_minutes=10, priority=Priority.HIGH, pet_id=luna.pet_id)
    luna.add_task(feeding)

    scheduler = Scheduler(owner=owner)

    assert scheduler.filter_tasks(pet_name="Mochi") == [walk]
    assert scheduler.filter_tasks(completed=False) == [feeding]
    assert scheduler.filter_tasks(completed=True) == [walk]


def test_mark_task_complete_schedules_next_occurrence_for_recurring_task():
    pet = Pet(name="Mochi", species="dog", owner_id="owner-1")
    task = Task(
        title="Morning walk",
        duration_minutes=30,
        priority=Priority.HIGH,
        pet_id=pet.pet_id,
        preferred_time=time(8, 0),
        recurrence="daily",
        due_date=date(2026, 1, 1),
    )
    pet.add_task(task)

    next_task = pet.mark_task_complete(task.task_id)

    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == date(2026, 1, 1) + timedelta(days=1)
    assert next_task in pet.get_tasks()


def test_mark_task_complete_does_not_recur_for_one_off_task():
    pet = Pet(name="Mochi", species="dog", owner_id="owner-1")
    task = Task(title="Vet visit", duration_minutes=45, priority=Priority.HIGH, pet_id=pet.pet_id)
    pet.add_task(task)

    next_task = pet.mark_task_complete(task.task_id)

    assert next_task is None
    assert len(pet.get_tasks()) == 1


def test_detect_conflicts_flags_tasks_at_the_same_preferred_time():
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog", owner_id=owner.owner_id)
    luna = Pet(name="Luna", species="cat", owner_id=owner.owner_id)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH, pet_id=mochi.pet_id, preferred_time=time(8, 0)))
    luna.add_task(Task(title="Vet checkup", duration_minutes=15, priority=Priority.HIGH, pet_id=luna.pet_id, preferred_time=time(8, 0)))
    luna.add_task(Task(title="Feeding", duration_minutes=10, priority=Priority.HIGH, pet_id=luna.pet_id, preferred_time=time(7, 30)))

    scheduler = Scheduler(owner=owner)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]
    assert "Morning walk" in conflicts[0]
    assert "Vet checkup" in conflicts[0]
