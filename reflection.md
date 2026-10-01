# PawPal+ Project Reflection

## 1. System Design

### a. Initial design

For my initial design, I decided to use four main classes: `Owner`, `Pet`, `Task`, and `Scheduler`.

* **Owner** represents the person using the app. It stores the owner's name and preferences and keeps track of their pets. It can also retrieve all of the owner's tasks.
* **Pet** represents an individual pet. It stores information such as the pet's name, species, and breed, along with the tasks that belong to that pet.
* **Task** represents something that needs to be done for a pet, such as feeding, walking, or giving medication. It stores the task title, duration, priority, preferred time, and whether it has been completed.
* **Scheduler** is responsible for organizing the tasks. It gets the tasks from the owner, removes completed tasks, and creates a schedule based on the available amount of time.

I wanted to keep the design fairly simple instead of creating a separate class for every type of pet care task. Different types of tasks can all be represented by the same `Task` class.

### b. Design changes

My design changed a little while I was working on the project. When I had the AI review my original skeleton, it pointed out that the IDs for owners, pets, and tasks needed to be useful for finding specific objects. I changed the IDs to use `uuid.uuid4()` so that each object automatically receives a unique ID.

I also changed `Priority` to an `IntEnum` with `LOW`, `MEDIUM`, and `HIGH`. This makes it easier to compare priorities when the scheduler needs to organize tasks.

Another change was adding `Owner.get_all_tasks()`. The scheduler needs to work with tasks from all of the owner's pets, so I thought it made more sense for the `Owner` class to handle gathering those tasks. This also keeps the scheduler from having to know exactly how pets store their tasks.

I considered using direct object references between `Task`, `Pet`, and `Owner`, but decided to keep the ID-based approach. Direct references would make the relationships more complicated because the objects would point back to each other. For this project, using IDs kept the classes easier to understand.

---

## 2. Scheduling Logic and Tradeoffs

### a. Constraints and priorities

The scheduler considers whether a task has already been completed, how long the task takes, its priority, and its preferred time.

I decided that completed tasks should not be included in the schedule because there is no reason to include something that has already been done. The scheduler also has an available time limit, so it should not create a schedule that takes longer than the owner's available time.

Priority and preferred time are useful for organizing the remaining tasks. Higher-priority tasks can be handled before lower-priority tasks, while preferred times help determine when a task should happen.

### b. Tradeoffs

One tradeoff in my scheduler is that it uses a fairly simple approach to filling the available time. It goes through the tasks in order and adds a task as long as it still fits within the time limit.

This is easy to understand and works well for a small pet-care application, but it does not always produce the theoretically optimal schedule. For example, a combination of several shorter tasks could sometimes use the available time better than one longer task. I chose the simpler approach because it makes the scheduler easier to understand and verify.

Another tradeoff is in `Scheduler.detect_conflicts()`. It only flags tasks whose `preferred_time` values match exactly, rather than checking whether their durations actually overlap. For example, a 30-minute task starting at 08:00 and a 20-minute task starting at 08:10 clearly overlap, but since their start times differ, my scheduler would not flag them as a conflict. A more thorough version would convert each task into a start/end time range and check those ranges for overlap instead of comparing a single timestamp. I chose the exact-match approach because it is much simpler to implement and reason about, and it still catches the most obvious case for a pet owner: two tasks that are both scheduled to start at the same moment.

---

## 3. AI Collaboration

### a. How I used AI

I used AI throughout the project as a coding assistant rather than having it make all of the decisions for me. I used it to brainstorm the classes, create the initial UML structure, review my class design, implement parts of the Python logic, and help write tests.

One of the most useful prompts was asking how the `Scheduler` should get tasks from the `Owner`. This led to the idea of having `Owner.get_all_tasks()` return the tasks from all of the owner's pets. That made the relationship between the classes clearer and also helped satisfy the multi-pet requirement.

I also found it useful to ask AI to explain errors and suggest simpler ways to write parts of the code instead of just asking it to rewrite everything.

### b. Judgment and verification

One suggestion I did not immediately accept was changing the ID fields into direct references between objects. While that could make some relationships easier to access, it would also make the objects more tightly connected and could create circular references.

I decided to keep the ID approach because it was simpler for this project. I also planned to verify the implementation by running the CLI program and automated tests instead of assuming that the generated code was correct.

This was useful because it reminded me that AI-generated code still needs to be checked by the person building the project.

### c. AI strategy across phases

The AI coding assistant feature I relied on most was its chat, used for design discussion and code review rather than one-shot generation. Asking it to review a skeleton or explain a tradeoff (like how `Scheduler` should reach an owner's tasks, or whether `detect_conflicts()` should check exact times or overlapping durations) produced more useful results than asking it to "build the feature," because it forced me to read and evaluate an explanation instead of just accepting a diff.

A second suggestion I modified rather than accepted outright came up while implementing `detect_conflicts()`. The AI's first version converted every task into a start/end time range and checked all pairs for overlap, which is the more "correct" approach. I simplified it down to an exact `preferred_time` match instead, documented in section 2b, because the interval-overlap version was harder to reason about and test for a feature whose main job, for this project, is catching the obvious case of two tasks booked at the same moment.

Splitting the work into separate chat sessions per phase (design/skeleton, backend implementation, testing, documentation/UI polish) helped more than I expected. Each chat stayed focused on one kind of question, so earlier design decisions (like the ID-based relationships) didn't get silently re-litigated or overridden while I was deep in an unrelated phase like writing tests or wiring up the Streamlit UI.

---

## 4. Testing and Verification

### a. What I tested

The suite in `tests/test_pawpal.py` grew to 12 tests covering the core behaviors and the smarter-scheduling features added in Phase 3:

* Basic task/pet behavior: `mark_complete()` flips a task's `completed` status, and adding a task increases a pet's task count.
* Sorting correctness: `Scheduler.sort_by_time()` returns tasks earliest-first, with no-preferred-time tasks pushed to the end instead of the start.
* Filtering: `Scheduler.filter_tasks()` narrows tasks by pet name and/or completion status, independently or together.
* Recurrence logic: completing a `"daily"` task schedules a new copy due one day later, completing a `"weekly"` task schedules one due seven days later, and a one-off task does not regenerate.
* Conflict detection: two tasks sharing a preferred time (across different pets) are flagged, and a conflict involving an already-completed task is correctly ignored.
* Edge cases: an owner with no pets, a pet with no tasks, and a time budget too small to fit every task all produce the right empty/partial result instead of raising an error.

These matter because they check the behaviors the rest of the app depends on: if tasks can't be reliably completed, sorted, or checked for conflicts, the schedule the `Scheduler` builds can't be trusted either.

### b. Confidence

My confidence in this suite is high for the behaviors it directly tests — sorting, filtering, recurrence, and the "obvious" conflict case are all exercised with both happy-path and edge-case inputs, and all 12 tests pass consistently (see the README's "Testing PawPal+" section for the actual `pytest` run).

The one place I'd stay cautious is `detect_conflicts()`: it is an intentionally simplified exact-time-match check rather than true overlapping-duration detection (see section 2b), so the tests confirm it does what it's designed to do, not that it catches every real-world double-booking.

---

## 5. Reflection

### a. What went well

I am most satisfied with how the classes work together. The `Owner` contains the pets, the pets contain their tasks, and the scheduler can get all of those tasks through the owner. This gives each class a fairly clear responsibility.

I also like the idea of testing the backend through the CLI before focusing on the Streamlit interface. It makes it easier to find problems with the actual logic before adding the UI.

### b. What I would improve

Conflict detection and recurring tasks are implemented now, but both still have room to grow. `detect_conflicts()` only catches exact `preferred_time` matches rather than true overlapping-duration conflicts (section 2b), and `build_schedule()` fills the available time greedily rather than searching for the combination of tasks that uses it best.

I would also add persistent storage so that pets and tasks survive restarting the Streamlit app instead of living only in `st.session_state` for the duration of a browser session.

### c. Key takeaway

The biggest thing I learned was that designing the structure of a program before writing all of the code makes implementation easier. The UML diagram gave me a clear idea of what each class was responsible for.

I also learned that using AI effectively does not mean accepting every piece of generated code. I still needed to understand the suggestions, decide whether they fit my design, and verify that the code actually worked. The AI was most useful when I used it to think through a problem or review my design rather than simply telling it to build the entire project for me.
