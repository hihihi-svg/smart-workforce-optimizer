import streamlit as st
from data import init_session_state
from importlib import reload

# Initialize session state first (must run before any streamlit operations)
init_session_state()

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go To",
    ["Home", "Employees", "Tasks", "Optimization", "Results"]
)

if page == "Home":
    from pages import home
    reload(home)
elif page == "Employees":
    from pages import employees
    reload(employees)
elif page == "Tasks":
    from pages import tasks
    reload(tasks)
elif page == "Optimization":
    from pages import optimization
    reload(optimization)
elif page == "Results":
    from pages import results
    reload(results)
