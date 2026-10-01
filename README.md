# PawPal+ (Module 2 Project)

PawPal+ is a Streamlit app designed to help pet owners keep track of their pets' daily care. The app can organize tasks such as walks, feeding, medication, and other activities into a daily schedule.

## Scenario

A busy pet owner may have several pets with different care needs. PawPal+ is designed to help organize those tasks while considering things like task priority, duration, preferred times, and the amount of time the owner has available.

The project was built in stages, starting with the Python backend and CLI demonstration before connecting the logic to the Streamlit interface.

## What I Built

The main goals of the project are to:

* Store information about an owner and their pets
* Add and manage pet care tasks
* Keep track of whether tasks have been completed
* Build a daily schedule from tasks belonging to multiple pets
* Consider task duration and the owner's available time
* Provide a readable schedule through the CLI
* Test the most important parts of the backend

## Features

* **Multi-pet task tracking** — an owner can have several pets, each with its own list of care tasks (`Owner`, `Pet`).
* **Priority- and time-aware schedule building** — `Scheduler.build_schedule()` fills the owner's available time with the highest-priority, earliest tasks first, skipping anything already completed.
* **Sorting by time** — `Scheduler.sort_by_time()` orders any list of tasks chronologically by `preferred_time`, pushing "anytime" tasks (no preferred time) to the end.
* **Filtering by pet/status** — `Scheduler.filter_tasks(pet_name=..., completed=...)` narrows the task list to one pet, one completion status, or both.
* **Daily/weekly recurrence** — marking a recurring task complete (`Pet.mark_task_complete()`) automatically schedules its next occurrence one day (`"daily"`) or seven days (`"weekly"`) later.
* **Conflict warnings** — `Scheduler.detect_conflicts()` flags any two incomplete tasks (even across different pets) that share the same preferred time, so a double-booking doesn't slip through.
* **CLI and Streamlit front ends** — the same `pawpal_system` logic layer powers both `main.py` (a scripted command-line demo) and `app.py` (an interactive Streamlit UI).

## Getting Started

### Setup

Create and activate a virtual environment:

```bash
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Install the required packages:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Suggested Workflow

The project was developed using a CLI-first approach:

1. Design the classes and relationships using UML.
2. Create the Python class skeletons.
3. Implement the backend logic in `pawpal_system.py`.
4. Test the backend using `main.py`.
5. Add automated tests with `pytest`.
6. Connect the backend to the Streamlit UI.
7. Continue improving the scheduling algorithms and UI.

## Implementation Summary

The main backend logic is contained in `pawpal_system.py`. It uses four classes that work together.

### `Task`

`Task` represents one pet-care activity. It stores:

* Task title
* Duration
* Priority
* Pet ID
* Optional preferred time
* Completion status

The `mark_complete()` and `mark_incomplete()` methods update the task's completion status.

### `Pet`

`Pet` represents an individual pet and stores its name, species, breed, and tasks.

The `add_task()` method adds a task to the pet, while `remove_task()` can remove a task using its ID. `get_tasks()` returns the pet's current tasks.

### `Owner`

`Owner` stores the owner's information and a list of their pets.

The `add_pet()` method adds a pet to the owner's profile. The `get_all_tasks()` method is especially important because it gathers tasks from all of the owner's pets into one list.

This allows the scheduler to work with multiple pets instead of only looking at one pet at a time.

### `Scheduler`

`Scheduler` is responsible for creating the daily plan.

It receives an `Owner` object and an available time limit. It gets the tasks by calling:

```python
owner.get_all_tasks()
```

The scheduler then ignores completed tasks and builds a schedule while staying within the available time.

The `explain_plan()` method formats the schedule into readable text for the CLI.

## 📸 Demo Walkthrough

### Streamlit UI features

Running `streamlit run app.py` gives the owner an interactive version of the same logic:

* An **owner name** field and an **Add pet** form (name, species, optional breed).
* An **Add task** form per pet, with duration, priority, optional preferred time, and a recurrence option (`never`/`daily`/`weekly`).
* A **filterable task table** (by pet and by status) that is sorted by preferred time via `Scheduler.sort_by_time()`, with status shown as ✅ Done / ⏳ Pending.
* A **conflict check** directly under the task table: `st.warning()` for each conflict found via `Scheduler.detect_conflicts()`, or `st.success("No scheduling conflicts detected.")` when there are none. This is placed right next to the task list — before the owner even builds a schedule — so a double-booking is visible the moment it's created, not buried behind a button click.
* Per-task **Done checkboxes** that call `Pet.mark_task_complete()`, which automatically schedules the next occurrence of a recurring task.
* A **Generate schedule** button that takes the owner's available minutes, calls `Scheduler.build_schedule()`, and shows the result with `st.success()` (total minutes used) and `st.table()` (the chosen tasks, time-ordered), with the full text explanation from `explain_plan()` tucked into an expander.

### Example workflow

1. Add a pet (e.g. "Mochi").
2. Add a task for that pet (e.g. "Morning walk", `HIGH` priority, preferred time `08:00`, repeats `daily`).
3. Add a second task for another pet at the same preferred time — the conflict warning appears immediately in the task table.
4. Check a recurring task off as "Done" — a new copy of it reappears in the table, due the next day.
5. Click **Generate schedule** to see the day's prioritized, time-sorted plan and how much of the available time it used.

### Sample CLI output

`main.py` demonstrates the same backend logic end-to-end — building a schedule, sorting, filtering, completing a recurring task, and detecting a conflict:

```bash
python main.py
```

```text
Today's Schedule:
  07:30 | Feeding (10 min) [priority: HIGH] - for Luna
  08:00 | Morning walk (30 min) [priority: HIGH] - for Mochi
  18:00 | Evening walk (20 min) [priority: MEDIUM] - for Mochi
Total: 60/60 minutes used

All tasks sorted by preferred time:
  07:30 | Feeding
  08:00 | Morning walk
  18:00 | Evening walk
  Anytime | Litter box cleaning

Mochi's tasks only:
  Evening walk
  Morning walk

Incomplete tasks only:
  Evening walk
  Morning walk
  Feeding
  Litter box cleaning

Completing the recurring 'Morning walk' task...
  Done! Next occurrence auto-scheduled for 2026-10-01 (daily).

Adding a conflicting task for Luna at 08:00 (same time as Mochi's next walk)...
  Warning(s):
  Conflict at 08:00: Morning walk (Mochi), Vet checkup (Luna)
```

## 🧪 Testing PawPal+

The project uses `pytest` for automated testing.

Run the tests with:

```bash
python -m pytest
```

The test suite (`tests/test_pawpal.py`, 12 tests) covers:

* **Core task/pet behavior** — `mark_complete()` changes a task's completion status; adding a task increases a pet's task count.
* **Sorting correctness** — `Scheduler.sort_by_time()` returns tasks in chronological order, with tasks that have no preferred time sorted to the end instead of the start.
* **Filtering** — `Scheduler.filter_tasks()` narrows tasks correctly by pet name and/or completion status.
* **Recurrence logic** — completing a `"daily"` task schedules a new, incomplete copy due one day later; completing a `"weekly"` task schedules one due seven days later; a one-off task (no recurrence) does not regenerate.
* **Conflict detection** — `Scheduler.detect_conflicts()` flags two tasks (across different pets) that share the same preferred time, and ignores conflicts where one of the tasks is already completed.
* **Edge cases** — an owner with no pets, and a pet with no tasks, both produce an empty schedule and no conflicts instead of raising; `build_schedule()` stops adding tasks once the available time budget is used up.

Example successful output:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\CodePath_Stuff\ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 12 items

tests\test_pawpal.py ............                                        [100%]

============================= 12 passed in 0.07s ==============================
```

### Confidence Level

⭐⭐⭐⭐☆ (4/5)

The core logic — task completion, sorting, filtering, recurrence, and conflict detection — is well covered and passes consistently, including the edge cases (no pets, no tasks, tight time budgets) called out in `reflection.md`. I'm holding back one star because `detect_conflicts()` is an intentionally simplified exact-time-match check rather than true overlapping-duration detection (see `reflection.md`, section 2b), so it's not tested against that more thorough behavior since the behavior itself doesn't exist yet.

## 📐 Smarter Scheduling

| Feature                    | Method                        | Current Status |
| -------------------------- | ------------------------------ | --------------- |
| Task collection            | `Owner.get_all_tasks()`        | Implemented      |
| Basic schedule building     | `Scheduler.build_schedule()`   | Implemented      |
| Completed-task filtering    | `Scheduler.build_schedule()`   | Implemented      |
| Available-time constraint   | `Scheduler.build_schedule()`   | Implemented      |
| Sorting by priority/time    | `Scheduler.build_schedule()`   | Implemented      |
| Sorting by time only        | `Scheduler.sort_by_time()`     | Implemented      |
| Filtering by pet/status     | `Scheduler.filter_tasks()`     | Implemented      |
| Conflict detection          | `Scheduler.detect_conflicts()` | Implemented      |
| Recurring tasks             | `Task.create_next_occurrence()`, `Pet.mark_task_complete()` | Implemented |

### Sorting

`Scheduler.sort_by_time()` returns tasks ordered by `preferred_time`, earliest first. Tasks with no preferred time are sorted to the end instead of the beginning, since they don't have an actual time slot. `Scheduler.build_schedule()` uses a similar, slightly richer sort: priority first (high before low), then preferred time.

### Filtering

`Scheduler.filter_tasks(pet_name=..., completed=...)` narrows the owner's tasks by pet name and/or completion status. Either filter can be omitted; with both omitted it returns every task. This is used, for example, to show only a specific pet's open tasks.

### Recurring tasks

A `Task` can carry a `recurrence` of `"daily"` or `"weekly"` plus a `due_date`. When `Pet.mark_task_complete(task_id)` is called, it marks the task complete and, if it recurs, calls `Task.create_next_occurrence()` to build a fresh, incomplete copy of the task with its `due_date` advanced by one day (daily) or seven days (weekly), then adds that copy back onto the pet automatically. One-off tasks (`recurrence=None`) are left alone.

### Conflict detection

`Scheduler.detect_conflicts()` groups the owner's incomplete tasks by `preferred_time` and returns a human-readable warning string for any time slot shared by two or more tasks, across any of the owner's pets. It returns an empty list when there are no conflicts and never raises, so a conflict never crashes the program. This is a lightweight, exact-time-match check — see `reflection.md` (section 2b) for the tradeoff versus true overlapping-duration detection.

## Project Files

```text
pawpal_system.py         # Main backend classes
main.py                  # CLI demonstration
app.py                   # Streamlit application
tests/test_pawpal.py     # Automated tests
diagrams/uml.mmd         # Initial UML draft (Phase 1)
diagrams/uml_final.mmd   # Final UML, matching the implemented classes/methods
reflection.md            # Project reflection
```
