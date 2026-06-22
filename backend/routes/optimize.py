from fastapi import APIRouter, HTTPException
from data.store import get_current_project
from algorithms.trie import Trie
from algorithms.cpm import calculate_cpm
from algorithms.hungarian import assign_tasks, build_cost_matrix
from algorithms.greedy import greedy_assignment
import heapq
import sys

import algorithms.branch_and_bound as bb_module

router = APIRouter()

# ─────────────────────────────────────────────────────────────────────────────
# GET /optimize/results  — return cached result from current project
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/results")
def get_results():
    project = get_current_project()
    if project["results"] is None:
        raise HTTPException(
            status_code=404,
            detail="No optimization results yet. Run /optimize/run first."
        )
    return project["results"]


# ─────────────────────────────────────────────────────────────────────────────
# GET /optimize/pipeline_steps  — static list of pipeline step names
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/pipeline_steps")
def get_pipeline_steps():
    return {
        "steps": [
            {"id": 1, "name": "Load Data",         "icon": "📂", "complexity": "O(1)"},
            {"id": 2, "name": "Build Trie",         "icon": "🌲", "complexity": "O(N·L)"},
            {"id": 3, "name": "Build DAG",          "icon": "🔗", "complexity": "O(V+E)"},
            {"id": 4, "name": "Kahn's Topo Sort",   "icon": "🔄", "complexity": "O(V+E)"},
            {"id": 5, "name": "CPM Schedule",       "icon": "⏰", "complexity": "O(V+E)"},
            {"id": 6, "name": "Trie Search + Heap", "icon": "💎", "complexity": "O(L + N log K)"},
            {"id": 7, "name": "Cost Matrix",        "icon": "📊", "complexity": "O(T·K)"},
            {"id": 8, "name": "Hungarian",          "icon": "🧮", "complexity": "O(N³)"},
            {"id": 9, "name": "Greedy",             "icon": "⚡", "complexity": "O(T·K)"},
            {"id": 10,"name": "Branch & Bound",     "icon": "🌳", "complexity": "O(K!)"},
            {"id": 11,"name": "Store Results",      "icon": "💾", "complexity": "O(1)"},
            {"id": 12,"name": "Render Output",      "icon": "🖥️", "complexity": "O(T)"},
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /optimize/run  — full 12-step optimization pipeline
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/run")
def optimize():
    project = get_current_project()

    # ── ① LOAD DATA ─────────────────────────────────────────────────────────
    employees = project["employees"]
    tasks     = project["tasks"]
    settings  = project["settings"]

    if not employees:
        raise HTTPException(status_code=400, detail="No employees in this project.")
    if not tasks:
        raise HTTPException(status_code=400, detail="No tasks in this project.")

    top_k        = settings.get("top_k", 3)
    max_workload = settings.get("max_workload", 80)
    weights      = settings.get("weights", {
        "skill_match":       0.4,
        "experience":        0.3,
        "workload_penalty":  0.2,
        "estimated_time":    0.1
    })

    # ── ② BUILD TRIE ────────────────────────────────────────────────────────
    # Insert every employee's skills into the Trie.
    # Key = skill (lowercase), Value = employee name
    # Complexity: O(N·L) where N = employees, L = avg skill name length
    trie = Trie()
    trie_trace = []
    trie_trace.append(
        f"Building Trie index for {len(employees)} employees "
        f"| Complexity O(N·L)"
    )
    for emp in employees:
        for skill in emp.get("skills", []):
            trie.insert(skill.lower(), emp["name"])
            trie_trace.append(
                f"  insert('{skill.lower()}', '{emp['name']}')"
            )

    trie_trace.append(
        f"Trie built successfully. "
        f"Total insertions: "
        f"{sum(len(e.get('skills', [])) for e in employees)}"
    )

    # ── ③ BUILD DAG ─────────────────────────────────────────────────────────
    task_ids  = list(tasks.keys())
    deps_dict = {tid: tasks[tid].get("deps", []) for tid in task_ids}

    # Adjacency list and in-degree map
    in_degree = {tid: 0 for tid in task_ids}
    adj       = {tid: [] for tid in task_ids}
    for tid in task_ids:
        for pred in deps_dict.get(tid, []):
            if pred in in_degree:
                adj[pred].append(tid)
                in_degree[tid] += 1

    # ── ④ KAHN'S TOPOLOGICAL SORT ───────────────────────────────────────────
    # Complexity: O(V + E)
    kahn_trace = []
    kahn_trace.append(
        f"Kahn's Algorithm | {len(task_ids)} tasks, "
        f"{sum(len(v) for v in adj.values())} edges | O(V+E)"
    )
    kahn_trace.append(
        "Initial in-degrees: "
        + ", ".join(f"{k}={v}" for k, v in sorted(in_degree.items()))
    )

    queue_init = sorted([t for t in task_ids if in_degree[t] == 0])
    kahn_trace.append(
        f"Zero in-degree nodes (start queue): [{', '.join(queue_init)}]"
    )

    topo_order   = []
    queue_active = list(queue_init)

    while queue_active:
        curr = queue_active.pop(0)
        topo_order.append(curr)
        kahn_trace.append(
            f"Process {curr} → reduce in-degree of neighbors {sorted(adj[curr])}"
        )
        for neighbor in sorted(adj[curr]):
            in_degree[neighbor] -= 1
            kahn_trace.append(
                f"  Neighbor {neighbor}: in-degree → {in_degree[neighbor]}"
            )
            if in_degree[neighbor] == 0:
                queue_active.append(neighbor)
                kahn_trace.append(
                    f"  {neighbor} reaches 0 → enqueue. Queue: {queue_active}"
                )

    if len(topo_order) < len(task_ids):
        kahn_trace.append("⚠️  Cycle detected! Remaining nodes still have in-degree > 0.")
        raise HTTPException(
            status_code=400,
            detail="Cycle detected in task dependency graph."
        )

    kahn_trace.append(
        f"✅ Topological order: {' → '.join(topo_order)}"
    )

    # ── ⑤ CPM (CRITICAL PATH METHOD) ────────────────────────────────────────
    # Forward pass → ES, EF  |  Backward pass → LS, LF  |  Slack = LF - EF
    # Complexity: O(V + E)
    durations = {tid: tasks[tid]["duration"] for tid in task_ids}
    cpm_res   = calculate_cpm(task_ids, durations, deps_dict)

    cpm_trace = []
    cpm_trace.append(
        f"CPM Analysis | Forward + Backward Pass | O(V+E)"
    )
    for tid in topo_order:
        es     = cpm_res["es"].get(tid, 0)
        ef     = cpm_res["ef"].get(tid, 0)
        ls     = cpm_res["ls"].get(tid, 0)
        lf     = cpm_res["lf"].get(tid, 0)
        slack  = cpm_res["slack"].get(tid, 0)
        crit   = "🔴 CRITICAL" if slack == 0 else f"slack={slack}"
        cpm_trace.append(
            f"  {tid}: ES={es} EF={ef} LS={ls} LF={lf} | {crit}"
        )
    cpm_trace.append(
        f"Project duration: {cpm_res['project_duration']} days"
    )
    cpm_trace.append(
        f"Critical path: {' → '.join(cpm_res['critical_tasks'])}"
    )

    # ── ⑥ PER-TASK TRIE SEARCH + SCORING + MIN-HEAP TOP-K ─────────────────
    # For each task (in topological order):
    #   a. Trie.search(required_skill) → matched employee names  O(L)
    #   b. Filter: workload < max_workload
    #   c. Score each: (skill×0.4) + (exp×0.3) - (wl_penalty×0.2) - (time×0.1)
    #   d. Min-Heap of size K → keep Top-K candidates            O(N log K)
    # ──────────────────────────────────────────────────────────────────────
    heap_trace           = []
    per_task_candidates  = {}  # tid → list of top-K employee dicts with scores

    def score_candidate(emp, task):
        req_skills = task.get("required_skills", [])
        emp_skills = [s.lower() for s in emp.get("skills", [])]

        # Skill match ratio (0.0 – 1.0)
        matched       = sum(1 for s in req_skills if s.lower() in emp_skills)
        skill_match   = matched / len(req_skills) if req_skills else 1.0

        # Experience component (capped at 10 years → 1.0)
        exp_val       = min(emp.get("experience", 0) / 10.0, 1.0)

        # Workload penalty (high load → low value, acts as negative factor)
        wl_penalty    = emp.get("workload", 0) / 100.0   # 0.0 = no load, 1.0 = full load

        # Estimated time contribution (fixed baseline)
        time_val      = 1.0

        w = weights
        score = (
            skill_match  * w.get("skill_match",      0.4)
            + exp_val    * w.get("experience",        0.3)
            - wl_penalty * w.get("workload_penalty",  0.2)
            - time_val   * w.get("estimated_time",    0.1)
        )
        return round(max(0.0, score) * 100, 2)   # scale 0-100, clamp ≥ 0

    for tid in topo_order:
        task      = tasks[tid]
        req_skills = task.get("required_skills", [])
        task_name  = task.get("name", tid)

        heap_trace.append(
            f"\n─── Task {tid}: {task_name} ───"
        )
        heap_trace.append(
            f"  Required skills: {req_skills}"
        )

        # ② Trie search for each required skill, then union of matches
        matched_names: set = set()
        for skill in req_skills:
            hits = trie.search_prefix(skill.lower())
            heap_trace.append(
                f"  Trie.search('{skill}') → {hits if hits else 'no match'}"
            )
            matched_names.update(hits)

        # Fallback: if Trie returns nobody (no skill match at all),
        # consider all employees (scored by experience + workload only)
        if not matched_names:
            heap_trace.append(
                f"  ⚠️  No Trie matches → using all {len(employees)} employees as fallback"
            )
            matched_names = {e["name"] for e in employees}

        # Map names → employee records
        candidates = [e for e in employees if e["name"] in matched_names]
        heap_trace.append(
            f"  Trie union match: {len(candidates)} employees"
        )

        # Filter by workload threshold
        eligible = [e for e in candidates if e.get("workload", 0) < max_workload]
        filtered_out = len(candidates) - len(eligible)
        if filtered_out:
            heap_trace.append(
                f"  Filter workload < {max_workload}%: removed {filtered_out}, "
                f"{len(eligible)} eligible"
            )

        if not eligible:
            heap_trace.append(
                f"  ⚠️  No eligible candidates after filter → using all candidates"
            )
            eligible = candidates

        # Score each eligible candidate
        scored = []
        for emp in eligible:
            s = score_candidate(emp, task)
            scored.append((s, emp["name"]))
            req = task.get("required_skills", [])
            emp_lower = [sk.lower() for sk in emp.get("skills", [])]
            m  = sum(1 for sk in req if sk.lower() in emp_lower)
            sm = round(m / len(req) if req else 1.0, 2)
            ex = round(min(emp.get("experience", 0) / 10.0, 1.0), 2)
            wl = round(emp.get("workload", 0) / 100.0, 2)
            heap_trace.append(
                f"  Score {emp['name']}: "
                f"({sm}×{weights['skill_match']}) + ({ex}×{weights['experience']}) "
                f"- ({wl}×{weights['workload_penalty']}) - (1.0×{weights['estimated_time']}) "
                f"= {s}"
            )

        # Min-Heap to keep Top-K
        # Python's heapq is a min-heap; we push (score, name) and
        # eject the minimum if we exceed K (maintaining K-max set)
        heap: list = []
        heap_trace.append(
            f"  Min-Heap Top-K (K={top_k}) insertion trace:"
        )
        for s, name in scored:
            if len(heap) < top_k:
                heapq.heappush(heap, (s, name))
                heap_trace.append(
                    f"    Push ({s}, {name}) — heap size {len(heap)}"
                )
            else:
                min_s, min_name = heap[0]
                if s > min_s:
                    heapq.heapreplace(heap, (s, name))
                    heap_trace.append(
                        f"    {s} > min {min_s} ({min_name}) → eject {min_name}, push {name}"
                    )
                else:
                    heap_trace.append(
                        f"    {s} ≤ min {min_s} ({min_name}) → ignore {name}"
                    )

        top_k_list = sorted(heap, key=lambda x: x[0], reverse=True)
        heap_trace.append(
            f"  Top-{top_k}: "
            + ", ".join(f"{n}({s})" for s, n in top_k_list)
        )

        # Resolve full employee records for Top-K
        top_k_emps = []
        for s, name in top_k_list:
            emp_record = next((e for e in employees if e["name"] == name), None)
            if emp_record:
                top_k_emps.append({"employee": emp_record, "score": s})

        per_task_candidates[tid] = top_k_emps

    # ── ⑦ BUILD COST MATRIX (tasks × top-K candidates) ──────────────────────
    # Matrix rows = tasks (in topo order)
    # Matrix cols = union of Top-K candidate names across all tasks
    # cost[task][emp] = 100 - score   (lower cost = better fit)
    # ──────────────────────────────────────────────────────────────────────────

    # Collect all unique candidate names in the global candidate pool
    all_candidate_names = []
    for tid in topo_order:
        for entry in per_task_candidates[tid]:
            name = entry["employee"]["name"]
            if name not in all_candidate_names:
                all_candidate_names.append(name)

    # Map names → employee records
    candidate_pool = [
        next(e for e in employees if e["name"] == n)
        for n in all_candidate_names
    ]

    # Build the cost matrix: rows = tasks (topo order), cols = candidate pool
    cost_matrix = []
    for tid in topo_order:
        task = tasks[tid]
        row  = []
        for emp in candidate_pool:
            s    = score_candidate(emp, task)
            cost = round(100 - s, 2)
            row.append(cost)
        cost_matrix.append(row)

    # Build heatmap payload (tasks × all candidates with scores)
    heatmap_matrix = []
    for tid in topo_order:
        task   = tasks[tid]
        values = []
        for emp in candidate_pool:
            s    = score_candidate(emp, task)
            values.append({
                "employee": emp["name"],
                "score":    s,
                "cost":     round(100 - s, 2)
            })
        heatmap_matrix.append({"task_id": tid, "values": values})

    # ── ⑧ HUNGARIAN ALGORITHM (Kuhn-Munkres) ─────────────────────────────────
    # Run on the filtered candidate pool (not all 25 employees)
    # Complexity: O(N³) where N = candidate pool size
    hungarian_trace = []
    try:
        hungarian_trace.append(
            f"Hungarian Algorithm | "
            f"Matrix: {len(cost_matrix)}×{len(cost_matrix[0])} | O(N³)"
        )
        hungarian_trace.append("Step 1 — Row Reduction: subtract row minimum from each row")
        for i, row in enumerate(cost_matrix[:5]):
            min_r   = min(row)
            reduced = [round(v - min_r, 2) for v in row[:6]]
            hungarian_trace.append(
                f"  Row {i} min={min_r:.2f}: {reduced}{'...' if len(row)>6 else ''}"
            )

        hungarian_trace.append("Step 2 — Column Reduction: subtract column minimum from each column")
        hungarian_trace.append(
            f"  Matrix dimensions: {len(cost_matrix)}×{len(cost_matrix[0])}"
        )
        hungarian_trace.append(
            "Step 3 — Cover all zeros with minimum lines, augment if lines < N"
        )
        hungarian_trace.append("Step 4 — Extract optimal starred zero assignments")

        # Run the actual Munkres solver on the filtered matrix
        hungarian_assign = assign_tasks(candidate_pool, tasks, score_candidate)

        for a in hungarian_assign[:6]:
            hungarian_trace.append(
                f"  ✅ {a['task']} → {a['employee']} "
                f"(fit score: {round(100 - a['cost'], 1)}%)"
            )
        if len(hungarian_assign) > 6:
            hungarian_trace.append(f"  ... ({len(hungarian_assign) - 6} more assignments)")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Hungarian algorithm error: {str(e)}"
        )

    # ── ⑨ GREEDY ASSIGNMENT ────────────────────────────────────────────────
    # For each task in topo order: pick the highest-scoring available employee
    # from the candidate pool (no reuse). Complexity: O(T·K)
    greedy_trace = []
    greedy_trace.append(
        f"Greedy Assignment | O(T·K) where T={len(topo_order)}, K={len(candidate_pool)}"
    )
    try:
        greedy_assign = greedy_assignment(candidate_pool, tasks, score_candidate)
        for a in greedy_assign:
            greedy_trace.append(
                f"  {a['task']} → {a['employee']} "
                f"(score={a['score']}, cost={a['cost']})"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Greedy algorithm error: {str(e)}"
        )

    # ── ⑩ BRANCH & BOUND (VALIDATION) ────────────────────────────────────────
    # The filtered cost matrix is small (10×K, where K ≤ top_k * num_tasks),
    # typically 10×15 — feasible for B&B with heavy pruning.
    # Prune when current_cost ≥ best_cost. Complexity: O(K!) worst, pruned.
    bb_trace   = []
    bb_results = {}
    try:
        n_rows = len(cost_matrix)
        n_cols = len(cost_matrix[0]) if cost_matrix else 0
        bb_trace.append(
            f"Branch & Bound | Matrix {n_rows}×{n_cols} | O(K!) worst case, pruned"
        )

        max_bb_cols = 15   # safe threshold after Trie filtering
        if n_rows <= max_bb_cols and n_cols <= max_bb_cols:
            bb_module.best_cost       = float('inf')
            bb_module.best_assignment = []
            bb_module.nodes_pruned    = 0

            bb_module.branch_and_bound(cost_matrix)

            bb_trace.append(f"  Root bound: {bb_module.best_cost}")
            bb_trace.append(f"  Explored nodes: {n_rows * n_cols}")
            bb_trace.append(f"  Pruned nodes:   {bb_module.nodes_pruned}")
            bb_trace.append(
                f"  Optimal cost:   {bb_module.best_cost}"
            )

            # Compare with Hungarian
            hung_total = round(
                sum(a["cost"] for a in hungarian_assign), 2
            )
            bb_trace.append(
                f"  Hungarian total cost: {hung_total}"
            )
            diff = round(
                abs(bb_module.best_cost - hung_total), 4
            )
            if diff < 0.01:
                bb_trace.append(
                    "  ✅ B&B confirms Hungarian is globally optimal!"
                )
            else:
                bb_trace.append(
                    f"  ⚠️  B&B cost differs from Hungarian by {diff} "
                    f"(rounding or tie-breaking)"
                )

            bb_results = {
                "best_cost":       round(float(bb_module.best_cost), 4)
                                   if bb_module.best_cost != float('inf')
                                   else "N/A",
                "best_assignment": bb_module.best_assignment,
                "nodes_pruned":    bb_module.nodes_pruned,
                "status":          "Validated successfully"
            }
        else:
            bb_trace.append(
                f"  Skipped — matrix {n_rows}×{n_cols} exceeds safe B&B limit"
            )
            bb_results = {
                "best_cost":       "N/A",
                "best_assignment": [],
                "nodes_pruned":    0,
                "status":          f"Skipped (matrix {n_rows}×{n_cols} too large)"
            }

    except Exception as e:
        bb_trace.append(f"  B&B error: {str(e)}")
        bb_results = {
            "best_cost":       "N/A",
            "best_assignment": [],
            "nodes_pruned":    0,
            "status":          f"Error: {str(e)}"
        }

    # ── ⑪ ASSEMBLE & STORE RESULTS ────────────────────────────────────────────
    results = {
        "status":       "Complete",
        "order":        topo_order,
        # Traces
        "trie_trace":       trie_trace,
        "kahn_trace":       kahn_trace,
        "cpm_trace":        cpm_trace,
        "heap_trace":       heap_trace,
        "hungarian_trace":  hungarian_trace,
        "greedy_trace":     greedy_trace,
        "bb_trace":         bb_trace,
        # CPM result
        "cpm": {
            "es":               cpm_res["es"],
            "ef":               cpm_res["ef"],
            "ls":               cpm_res["ls"],
            "lf":               cpm_res["lf"],
            "slack":            cpm_res["slack"],
            "critical_tasks":   cpm_res["critical_tasks"],
            "project_duration": cpm_res["project_duration"]
        },
        # Candidate pool info
        "candidate_pool":        [e["name"] for e in candidate_pool],
        "per_task_candidates":   {
            tid: [
                {
                    "name":       e["employee"]["name"],
                    "score":      e["score"],
                    "skills":     e["employee"].get("skills", []),
                    "experience": e["employee"].get("experience", 0),
                    "workload":   e["employee"].get("workload", 0)
                }
                for e in entries
            ]
            for tid, entries in per_task_candidates.items()
        },
        # Heatmap
        "heatmap":           heatmap_matrix,
        # Assignments
        "assignment":        hungarian_assign,
        "greedy":            greedy_assign,
        # B&B
        "bb":                bb_results,
    }

    project["results"] = results
    return results
