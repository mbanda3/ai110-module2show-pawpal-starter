"""CLI demo for the PawPal+ logic layer.

Creates an owner with two pets and several tasks, then builds and prints a
daily schedule. Run with: python main.py
"""

from datetime import time

from pawpal_system import Owner, Pet, Priority, Scheduler, Task

owner = Owner(name="Jordan")

mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu", owner_id=owner.owner_id)
luna = Pet(name="Luna", species="cat", breed="Tabby", owner_id=owner.owner_id)
owner.add_pet(mochi)
owner.add_pet(luna)

mochi.add_task(
    Task(
        title="Morning walk",
        duration_minutes=30,
        priority=Priority.HIGH,
        pet_id=mochi.pet_id,
        preferred_time=time(8, 0),
    )
)
mochi.add_task(
    Task(
        title="Evening walk",
        duration_minutes=20,
        priority=Priority.MEDIUM,
        pet_id=mochi.pet_id,
        preferred_time=time(18, 0),
    )
)
luna.add_task(
    Task(
        title="Feeding",
        duration_minutes=10,
        priority=Priority.HIGH,
        pet_id=luna.pet_id,
        preferred_time=time(7, 30),
    )
)
luna.add_task(
    Task(
        title="Litter box cleaning",
        duration_minutes=10,
        priority=Priority.LOW,
        pet_id=luna.pet_id,
    )
)

scheduler = Scheduler(owner=owner, available_minutes=60)
schedule = scheduler.build_schedule()

print(scheduler.explain_plan(schedule))
