import streamlit as st

st.title("Employee Management")

# Display current employees from session state
st.write("### Current Workforce Profiles")
st.dataframe(st.session_state.employees, use_container_width=True)

# Add new employee form
st.write("### Add New Employee")
with st.form("add_employee_form"):
    name = st.text_input("Name", placeholder="e.g. Rajesh Kumar")
    skills_raw = st.text_input("Skills (comma-separated)", placeholder="e.g. Python, SQL, ML")
    experience = st.number_input("Experience (years)", min_value=0, max_value=40, value=2)
    workload = st.slider("Current Workload (%)", min_value=0, max_value=100, value=30)
    
    submitted = st.form_submit_button("Add Employee")
    if submitted:
        if name:
            skills = [s.strip() for s in skills_raw.split(",") if s.strip()]
            new_emp = {
                "name": name,
                "skills": skills,
                "experience": int(experience),
                "workload": int(workload)
            }
            st.session_state.employees.append(new_emp)
            st.success(f"Added employee {name} successfully!")
            st.rerun()
        else:
            st.error("Please enter a valid employee name.")
