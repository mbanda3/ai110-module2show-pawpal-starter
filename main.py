"""CLI demo for the PawPal+ logic layer.

Creates an owner with two pets and several tasks, then builds and prints a
daily schedule. Also demonstrates the Phase 3 "smart scheduling" features:
sorting, filtering, recurring tasks, and conflict detection. Run with:
python main.py
"""

from datetime import time

from pawpal_system import Owner, Pet, Priority, Scheduler, Task

owner = Owner(name="Jordan")

mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu", owner_id=owner.owner_id)
luna = Pet(name="Luna", species="cat", breed="Tabby", owner_id=owner.owner_id)
owner.add_pet(mochi)
owner.add_pet(luna)

# Tasks are added out of time order on purpose, to show that sorting isn't
# just relying on insertion order.
evening_walk = Task(
    title="Evening walk",
    duration_minutes=20,
    priority=Priority.MEDIUM,
    pet_id=mochi.pet_id,
    preferred_time=time(18, 0),
)
mochi.add_task(evening_walk)

morning_walk = Task(
    title="Morning walk",
    duration_minutes=30,
    priority=Priority.HIGH,
    pet_id=mochi.pet_id,
    preferred_time=time(8, 0),
    recurrence="daily",
)
mochi.add_task(morning_walk)

feeding = Task(
    title="Feeding",
    duration_minutes=10,
    priority=Priority.HIGH,
    pet_id=luna.pet_id,
    preferred_time=time(7, 30),
)
luna.add_task(feeding)

litter_box = Task(
    title="Litter box cleaning",
    duration_minutes=10,
    priority=Priority.LOW,
    pet_id=luna.pet_id,
)
luna.add_task(litter_box)

scheduler = Scheduler(owner=owner, available_minutes=60)
schedule = scheduler.build_schedule()

print(scheduler.explain_plan(schedule))

# --- Sorting -----------------------------------------------------------
print("\nAll tasks sorted by preferred time:")
for task in scheduler.sort_by_time(owner.get_all_tasks()):
    time_label = task.preferred_time.strftime("%H:%M") if task.preferred_time else "Anytime"
    print(f"  {time_label} | {task.title}")

# --- Filtering -----------------------------------------------------------
print("\nMochi's tasks only:")
for task in scheduler.filter_tasks(pet_name="Mochi"):
    print(f"  {task.title}")

print("\nIncomplete tasks only:")
for task in scheduler.filter_tasks(completed=False):
    print(f"  {task.title}")

# --- Recurring tasks -----------------------------------------------------
print("\nCompleting the recurring 'Morning walk' task...")
next_walk = mochi.mark_task_complete(morning_walk.task_id)
if next_walk is not None:
    print(f"  Done! Next occurrence auto-scheduled for {next_walk.due_date} ({next_walk.recurrence}).")

# --- Conflict detection ----------------------------------------------------
print("\nAdding a conflicting task for Luna at 08:00 (same time as Mochi's next walk)...")
conflicting_task = Task(
    title="Vet checkup",
    duration_minutes=15,
    priority=Priority.HIGH,
    pet_id=luna.pet_id,
    preferred_time=time(8, 0),
)
luna.add_task(conflicting_task)

conflicts = scheduler.detect_conflicts()
if conflicts:
    print("  Warning(s):")
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("  No conflicts detected.")
