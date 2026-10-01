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

---

## 4. Testing and Verification

### a. What I tested

I created tests for two basic behaviors.

First, I tested that calling `mark_complete()` changes a task's `completed` value from `False` to `True`.

Second, I tested that adding a task to a pet increases the number of tasks associated with that pet.

These tests are important because they check two of the basic behaviors that the rest of the application depends on. If tasks cannot be completed or added correctly, the scheduler would not have reliable information to work with.

### b. Confidence

I expect the basic functionality to work because the classes have relatively simple responsibilities, but I would still verify everything by running the CLI program and the automated tests.

There are also several edge cases that I would test if I had more time. For example, I would test an owner with no pets, a pet with no tasks, multiple tasks with the same preferred time, tasks that are longer than the available time, and tasks with no preferred time.

I would also add more tests once the scheduling algorithms for recurring tasks and conflict detection are implemented.

---

## 5. Reflection

### a. What went well

I am most satisfied with how the classes work together. The `Owner` contains the pets, the pets contain their tasks, and the scheduler can get all of those tasks through the owner. This gives each class a fairly clear responsibility.

I also like the idea of testing the backend through the CLI before focusing on the Streamlit interface. It makes it easier to find problems with the actual logic before adding the UI.

### b. What I would improve

If I had another iteration, I would improve the scheduling algorithm. The current version is intentionally simple, and there are several ways it could become more useful. For example, it could detect conflicting tasks, handle recurring tasks, and provide more detailed scheduling decisions.

I would also consider adding more persistent storage so that pets and tasks are not lost when the application is restarted.

### c. Key takeaway

The biggest thing I learned was that designing the structure of a program before writing all of the code makes implementation easier. The UML diagram gave me a clear idea of what each class was responsible for.

I also learned that using AI effectively does not mean accepting every piece of generated code. I still needed to understand the suggestions, decide whether they fit my design, and verify that the code actually worked. The AI was most useful when I used it to think through a problem or review my design rather than simply telling it to build the entire project for me.
