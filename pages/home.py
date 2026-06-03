import streamlit as st

st.title("Smart Workforce Assignment Optimizer")
st.write("Optimize workforce assignments and schedule task dependencies using DAA algorithms.")

# Compute dynamic statistics from session state
num_employees = len(st.session_state.employees)
num_tasks = len(st.session_state.tasks)

# Check if optimization results are already present in session state
results = st.session_state.get("optimization_results", None)
num_critical = 0
avg_workload = 0

if num_employees > 0:
    avg_workload = int(sum(e.get("workload", 0) for e in st.session_state.employees) / num_employees)

if results and "cpm" in results:
    num_critical = len(results["cpm"].get("critical_tasks", []))

col1, col2, col3, col4 = st.columns(4)

col1.metric("Employees", num_employees)
col2.metric("Tasks", num_tasks)
col3.metric("Critical Tasks", num_critical if num_critical > 0 else "Run CPM")
col4.metric("Avg Workload", f"{avg_workload}%")

st.markdown("### Next Steps")
st.write("Go to the **Optimization** page from the sidebar to run the workforce assignment and schedule calculations.")
