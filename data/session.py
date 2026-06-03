import streamlit as st
from data.employees import employees as default_employees
from data.tasks import tasks as default_tasks

def init_session_state():
    if "employees" not in st.session_state:
        st.session_state.employees = [dict(emp) for emp in default_employees]
    if "tasks" not in st.session_state:
        st.session_state.tasks = {k: dict(v) for k, v in default_tasks.items()}
    if "optimization_results" not in st.session_state:
        st.session_state.optimization_results = None
