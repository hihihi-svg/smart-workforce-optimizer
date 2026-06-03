import streamlit as st

st.title("Optimization Results")

results = st.session_state.get("optimization_results", None)

if results is None or not results:
    st.warning("No optimization results found. Please go to the **Optimization** page and run the algorithms first.")
else:
    # 1. Show CPM Scheduling if present
    if "cpm" in results:
        st.write("### 1. Project Scheduling (CPM)")
        cpm = results["cpm"]
        st.write(f"**Total Project Duration:** {cpm['duration']} days")
        st.write(f"**Critical Tasks (Zero Float/Slack):** {', '.join(cpm['critical_tasks'])}")
        
        st.write("**Earliest Finish Times:**")
        st.write(cpm["earliest_finish"])
    else:
        st.info("ℹ CPM Schedule has not been run yet. Run it on the **Optimization** page.")
        
    # 2. Show Resource Matching if present
    if "hungarian" in results and "greedy" in results:
        st.write("### 2. Resource Matching (Hungarian vs Greedy)")
        col1, col2 = st.columns(2)
        
        h_total_score = 0
        with col1:
            st.subheader("Hungarian (Optimal)")
            h_data = []
            for assign in results["hungarian"]:
                cost = assign["cost"]
                score = 100 - cost
                h_total_score += score
                h_data.append({
                    "Task": assign["task"],
                    "Employee": assign["employee"],
                    "Suitability Score": f"{score:.2f}%"
                })
            st.table(h_data)
            st.write(f"**Total Combined Score:** {h_total_score:.2f}%")
            
        g_total_score = 0
        with col2:
            st.subheader("Greedy (Local Heuristic)")
            g_data = []
            for assign in results["greedy"]:
                score = assign["score"]
                g_total_score += score
                g_data.append({
                    "Task": assign["task"],
                    "Employee": assign["employee"],
                    "Suitability Score": f"{score:.2f}%"
                })
            st.table(g_data)
            st.write(f"**Total Combined Score:** {g_total_score:.2f}%")
            
        # 3. Show B&B Validation if present
        if "bb" in results:
            st.write("### 3. Optimal Validation (Branch & Bound)")
            bb = results["bb"]
            st.write(f"**Branch & Bound Optimal Cost:** {bb['best_cost']}")
            st.write(f"**B&B Optimal Index Mapping:** {bb['best_assignment']}")
            st.write(f"**Nodes Pruned (Saved Calculations):** {bb['nodes_pruned']}")
            
        # 4. Summary Analysis
        st.write("### 4. Summary Analysis")
        # Estimate number of tasks dynamically to get correct max cost metric
        num_tasks = len(results["hungarian"])
        max_possible_score = num_tasks * 100
        
        h_cost = max_possible_score - h_total_score
        g_cost = max_possible_score - g_total_score
        
        st.write(f"Hungarian Cost Value: {h_cost:.2f}")
        st.write(f"Greedy Cost Value: {g_cost:.2f}")
        
        if g_cost > h_cost:
            pct_improvement = ((g_cost - h_cost) / g_cost) * 100
            st.success(f"💡 Hungarian outperforms Greedy by **{pct_improvement:.1f}%** (Lower total cost index of {h_cost:.2f} vs {g_cost:.2f}).")
        else:
            st.info("💡 Greedy heuristics matched the optimal Hungarian allocation in this specific instance.")
    else:
        st.info("ℹ Resource Assignment has not been run yet. Run it on the **Optimization** page.")
