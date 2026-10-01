from datetime import time as dt_time

import streamlit as st

from pawpal_system import Owner, Pet, Priority, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+. Add your pets, give them care tasks, and generate a
prioritized daily schedule powered by the `pawpal_system` logic layer.
"""
)

with st.expander("Scenario"):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

# The Owner is created once per browser session and reused on every rerun,
# so pets/tasks added earlier in the session aren't lost when a widget fires.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner: Owner = st.session_state.owner

st.divider()
owner.name = st.text_input("Owner name", value=owner.name)

st.subheader("Pets")

with st.form("add_pet_form", clear_on_submit=True):
    st.markdown("**Add a pet**")
    col1, col2, col3 = st.columns(3)
    with col1:
        new_pet_name = st.text_input("Pet name", key="new_pet_name")
    with col2:
        new_pet_species = st.selectbox("Species", ["dog", "cat", "other"], key="new_pet_species")
    with col3:
        new_pet_breed = st.text_input("Breed (optional)", key="new_pet_breed")

    if st.form_submit_button("Add pet") and new_pet_name:
        pet = Pet(
            name=new_pet_name,
            species=new_pet_species,
            owner_id=owner.owner_id,
            breed=new_pet_breed or None,
        )
        owner.add_pet(pet)

if not owner.get_pets():
    st.info("No pets yet. Add one above.")
else:
    st.write("Current pets:", ", ".join(pet.name for pet in owner.get_pets()))

st.divider()

st.subheader("Tasks")

if owner.get_pets():
    with st.form("add_task_form", clear_on_submit=True):
        st.markdown("**Add a task**")
        pet_options = {pet.name: pet for pet in owner.get_pets()}
        selected_pet_name = st.selectbox("For which pet?", list(pet_options.keys()), key="task_pet")
        task_title = st.text_input("Task title", value="Morning walk", key="task_title")

        col1, col2, col3 = st.columns(3)
        with col1:
            duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240, value=20, key="task_duration"
            )
        with col2:
            priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2, key="task_priority")
        with col3:
            recurrence_label = st.selectbox("Repeats", ["never", "daily", "weekly"], key="task_recurrence")

        has_preferred_time = st.checkbox("Set preferred time?", key="task_has_time")
        preferred_time = None
        if has_preferred_time:
            preferred_time = st.time_input("Preferred time", value=dt_time(8, 0), key="task_time")

        if st.form_submit_button("Add task") and task_title:
            pet = pet_options[selected_pet_name]
            task = Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=Priority[priority_label.upper()],
                pet_id=pet.pet_id,
                preferred_time=preferred_time,
                recurrence=None if recurrence_label == "never" else recurrence_label,
            )
            pet.add_task(task)
else:
    st.info("Add a pet first before adding tasks.")

if owner.get_all_tasks():
    scheduler = Scheduler(owner=owner)
    pet_names = {pet.pet_id: pet.name for pet in owner.get_pets()}

    st.markdown("**Filter tasks**")
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        pet_filter_options = ["All pets"] + [pet.name for pet in owner.get_pets()]
        pet_filter = st.selectbox("Pet", pet_filter_options, key="task_filter_pet")
    with filter_col2:
        status_filter = st.selectbox("Status", ["All", "Incomplete", "Completed"], key="task_filter_status")

    filtered_tasks = scheduler.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed=None if status_filter == "All" else status_filter == "Completed",
    )
    # Sorted by preferred time so the table reads like an actual daily agenda.
    sorted_tasks = scheduler.sort_by_time(filtered_tasks)

    if sorted_tasks:
        st.table(
            [
                {
                    "Pet": pet_names.get(task.pet_id, "Unknown"),
                    "Task": task.title,
                    "Time": task.preferred_time.strftime("%H:%M") if task.preferred_time else "Anytime",
                    "Duration (min)": task.duration_minutes,
                    "Priority": task.priority.name,
                    "Repeats": task.recurrence or "—",
                    "Status": "✅ Done" if task.completed else "⏳ Pending",
                }
                for task in sorted_tasks
            ]
        )
    else:
        st.info("No tasks match this filter.")

    # Conflicts are surfaced here, right next to the task list, so an owner
    # notices a double-booking while editing tasks instead of only finding
    # out after clicking "Generate schedule".
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.warning(f"⚠️ {len(conflicts)} scheduling conflict(s) detected:")
        for warning in conflicts:
            st.warning(warning)
    else:
        st.success("No scheduling conflicts detected.")

    st.markdown("**Mark tasks complete**")
    for pet in owner.get_pets():
        pet_tasks = scheduler.sort_by_time(pet.get_tasks())
        if not pet_tasks:
            continue
        st.markdown(f"_{pet.name}_")
        for task in pet_tasks:
            label_col, done_col = st.columns([4, 1])
            with label_col:
                label = f"{task.title} — {task.duration_minutes} min, {task.priority.name}"
                if task.preferred_time:
                    label += f", {task.preferred_time.strftime('%H:%M')}"
                if task.recurrence:
                    label += f", repeats {task.recurrence}"
                st.write(label)
            with done_col:
                is_done = st.checkbox("Done", value=task.completed, key=f"done_{task.task_id}")
                if is_done and not task.completed:
                    pet.mark_task_complete(task.task_id)
                elif not is_done and task.completed:
                    task.mark_incomplete()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
available_minutes = st.number_input(
    "Available minutes today", min_value=10, max_value=1440, value=480, step=10
)

if st.button("Generate schedule"):
    scheduler = Scheduler(owner=owner, available_minutes=int(available_minutes))
    schedule = scheduler.build_schedule()
    pet_names = {pet.pet_id: pet.name for pet in owner.get_pets()}

    if schedule:
        total_minutes = sum(task.duration_minutes for task in schedule)
        st.success(
            f"Scheduled {len(schedule)} task(s) — {total_minutes}/{int(available_minutes)} minutes used."
        )
        st.table(
            [
                {
                    "Time": task.preferred_time.strftime("%H:%M") if task.preferred_time else "Anytime",
                    "Task": task.title,
                    "Pet": pet_names.get(task.pet_id, "Unknown"),
                    "Duration (min)": task.duration_minutes,
                    "Priority": task.priority.name,
                }
                for task in schedule
            ]
        )
        with st.expander("Full explanation"):
            st.code(scheduler.explain_plan(schedule))
    else:
        st.info("No tasks were scheduled.")

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.warning("Heads up — some of today's tasks share the same preferred time:")
        for warning in conflicts:
            st.warning(warning)
