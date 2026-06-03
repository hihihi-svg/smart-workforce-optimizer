import streamlit as st

st.title("Task Management")

# Display current tasks from session state (formatted nicely as a table)
st.write("### Project Tasks")
task_list = []
for task_id, info in st.session_state.tasks.items():
    task_list.append({
        "Task ID": task_id,
        "Required Skills": ", ".join(info.get("required_skills", [])),
        "Duration (Days)": info.get("duration", 0),
        "Dependencies": ", ".join(info.get("deps", []))
    })
st.dataframe(task_list, use_container_width=True)

# Add new task form
st.write("### Add New Task")
with st.form("add_task_form"):
    task_id = st.text_input("Task ID (e.g. T5)", placeholder="e.g. T5")
    required_skills_raw = st.text_input("Required Skills (comma-separated)", placeholder="e.g. Python, ML")
    duration = st.number_input("Duration (days)", min_value=1, max_value=100, value=3)
    
    # Selection of potential dependencies from existing tasks
    existing_task_ids = list(st.session_state.tasks.keys())
    deps_raw = st.text_input("Dependencies (comma-separated task IDs, e.g. T1, T2)", placeholder="e.g. T1, T2")
    
    submitted = st.form_submit_button("Add Task")
    if submitted:
        if task_id:
            # Check for duplicate Task ID
            if task_id in st.session_state.tasks:
                st.error(f"Task ID {task_id} already exists.")
            else:
                req_skills = [s.strip() for s in required_skills_raw.split(",") if s.strip()]
                deps = [d.strip() for d in deps_raw.split(",") if d.strip() and d.strip() in existing_task_ids]
                
                st.session_state.tasks[task_id] = {
                    "required_skills": req_skills,
                    "duration": int(duration),
                    "deps": deps
                }
                st.success(f"Added task {task_id} successfully!")
                st.rerun()
        else:
            st.error("Please enter a valid Task ID.")
