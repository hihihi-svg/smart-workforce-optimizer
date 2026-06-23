import streamlit as st
from algorithms.topological_sort import topological_sort
from algorithms.cpm import critical_path
from algorithms.hungarian import assign_tasks
from algorithms.scorer import calculate_score

st.title("Optimization Pipeline")

# Load employees and tasks from session state
employees = st.session_state.employees
tasks = st.session_state.tasks

if st.button("Generate Task Order"):
    try:
        order = topological_sort(tasks)
        st.session_state.last_order = order
        st.write("Topological Order:")
        st.write(order)
    except ValueError as e:
        st.error(f"Cycle Detected: {e}")

if st.button("Run CPM"):
    try:
        order = topological_sort(tasks)
        if order == "Cycle Detected":
            st.error("Cannot run CPM: Cycle Detected in task dependencies.")
        else:
            ef, duration, critical = critical_path(tasks, order)
            st.write("Earliest Finish times:", ef)
            st.write("Project Duration:", duration)
            st.write("Critical Tasks:", critical)
            
            # Save results in session state for Results page
            if st.session_state.optimization_results is None:
                st.session_state.optimization_results = {}
            st.session_state.optimization_results["topo"] = order
            st.session_state.optimization_results["cpm"] = {
                "earliest_finish": ef,
                "duration": duration,
                "critical_tasks": critical
            }
    except Exception as e:
        st.error(f"Error running CPM: {e}")

if st.button("Run Resource Assignment"):
    try:
        assignments = assign_tasks(employees, tasks, calculate_score)
        st.write("Optimal Assignments:")
        st.write(assignments)
        
        # Save results in session state for Results page
        if st.session_state.optimization_results is None:
            st.session_state.optimization_results = {}
        st.session_state.optimization_results["hungarian"] = assignments
        
        # Also run greedy internally to keep Results page populated
        from algorithms.greedy import greedy_assignment
        
        greedy_assignments = greedy_assignment(employees, tasks, calculate_score)
        st.session_state.optimization_results["greedy"] = greedy_assignments
    except Exception as e:
        st.error(f"Error assigning tasks: {e}")
