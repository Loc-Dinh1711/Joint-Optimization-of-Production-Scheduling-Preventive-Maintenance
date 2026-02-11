# Sensitivity analysis of MILP for Weekly Production Target
import pulp 
 
# Constants 
processing_time = {  # Processing times in seconds 
    "Grinder": 18.00, 
    "VTD": 18.79, 
    "CHT": 34.95 
} 
pm_duration = {  # Preventive maintenance durations in seconds 
    "Grinder": 3 * 3600, 
    "VTD": 2 * 3600, 
    "CHT": 1.5 * 3600 
} 
available_time = 7 * 24 * 3600  # Total available time in seconds 
machines = ["Grinder", "VTD", "CHT"]  # Machine names 
 
 
# Function to build and solve MILP for a given production target 
def build_and_solve_milp(panels_per_week, processing_time, 
pm_duration): 
    # Calculate net available time 
    total_pm_time = sum(pm_duration.values()) 
    net_available_time = available_time - total_pm_time 
 
    # Initialize model 
    model = pulp.LpProblem("Minimize_Makespan", pulp.LpMinimize) 
 
    # Decision variables 
    C_max = pulp.LpVariable("C_max", lowBound=0, cat="Continuous")  # Makespan 
    C = pulp.LpVariable.dicts( 
        "Completion_Time", 
        ((i, m) for i in range(1, panels_per_week + 1) for m in machines), 
        lowBound=0, 
        cat="Continuous" 
    )  # Completion times 
    Y = pulp.LpVariable.dicts("PM_Schedule", machines, cat="Binary")  # Preventive maintenance scheduling 
    T_PM = pulp.LpVariable.dicts("PM_Start_Time", machines, lowBound=0, cat="Continuous")  # Start time of PM 
 
    # Objective: Minimize makespan 
    model += C_max, "Minimize_Makespan" 
 
    # Constraints 
    for i in range(1, panels_per_week + 1): 
        for m_idx, m in enumerate(machines): 
            if m_idx == 0:  # First machine (Grinder) 
                model += C[(i, m)] >= (i - 1) * processing_time[m], f"Start_Grinder_Panel_{i}" 
            else: 
                prev_machine = machines[m_idx - 1] 
                model += C[(i, m)] >= C[(i, prev_machine)] + processing_time[m], f"Sequence_{m}_Panel_{i}" 
 
            if i > 1: 
                model += C[(i, m)] >= C[(i - 1, m)] + processing_time[m], f"No_Overlap_{m}_Panel_{i}" 
 
    for i in range(1, panels_per_week + 1): 
        model += C_max >= C[(i, "CHT")], f"Makespan_Panel_{i}" 
 
    for m in machines: 
        model += Y[m] == 1, f"PM_Frequency_{m}" 
        model += T_PM[m] + pm_duration[m] <= net_available_time, f"PM_Availability_{m}" 
        for i in range(1, panels_per_week + 1): 
            model += T_PM[m] >= C[(i, m)] + processing_time[m], f"PM_Start_After_Production_{m}_Panel_{i}" 
 
    # Solve the model 
    solver = pulp.PULP_CBC_CMD() 
    model.solve(solver) 
 
    # Return results 
    if pulp.LpStatus[model.status] == "Optimal": 
        return pulp.value(C_max) / 3600  # Convert seconds to hours 
    else: 
        return None 
 
 
# Perform sensitivity analysis for Weekly Production Target 
def sensitivity_analysis_weekly_target(target_values): 
    results = [] 
    for target in target_values: 
        makespan = build_and_solve_milp(target, processing_time, pm_duration) 
        results.append({ 
            "Weekly_Production_Target": target, 
            "Makespan (hours)": makespan 
        }) 
    return results 
 
 
# Define range of Weekly Production Target values 
weekly_target_values = [14000, 14500, 15000, 15294, 16000, 16500] 
 
# Perform sensitivity analysis 
sensitivity_results = sensitivity_analysis_weekly_target(weekly_target_values) 
 
# Print results 
print("Sensitivity Analysis for Weekly Production Target:") 
for result in sensitivity_results: 
    print(f"Weekly Production Target: {result['Weekly_Production_Target']}, Makespan (hours): {result['Makespan (hours)']}")