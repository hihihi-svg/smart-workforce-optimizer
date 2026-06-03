import streamlit as st
from algorithms.trie import Trie

trie = Trie()

# Index employees from session state to keep it interactive
for emp in st.session_state.employees:
    for skill in emp["skills"]:
        trie.insert(skill, emp["name"])

st.title("Skill Search")

skill = st.text_input("Enter Skill Prefix")

if skill:
    result = trie.search_prefix(skill)
    st.write("Matching Employees:", result)
