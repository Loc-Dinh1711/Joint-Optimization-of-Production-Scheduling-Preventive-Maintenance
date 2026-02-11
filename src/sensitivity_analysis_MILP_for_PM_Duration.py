# Sensitivity analysis of MILP for PM Duration
import pulp 
 
# Constants 
panels_per_week = 15294  # Weekly production target 
processing_time = {  # Processing times in seconds 
    "Grinder": 18.00, 
    "VTD": 18.79, 
    "CHT": 34.95 
} 
available_time = 7 * 24 * 3600  # Total available time in seconds 
machines = ["Grinder", "VTD", "CHT"]  # Machine names 
 
# Function to build and solve MILP for a given PM duration 
def build_and_solve_milp_with_pm_duration(pm_duration): 
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
  
# Perform sensitivity analysis for PM Duration 
def sensitivity_analysis_pm_duration(machine, pm_durations): 
    results = [] 
    original_pm_duration = { 
        "Grinder": 3.0 * 3600, 
        "VTD": 2.0 * 3600, 
        "CHT": 1.5 * 3600 
    } 
    for duration in pm_durations: 
        pm_duration = original_pm_duration.copy() 
        pm_duration[machine] = duration  # Update PM duration for the specific machine 
        makespan = build_and_solve_milp_with_pm_duration(pm_duration) 
        results.append({ 
            "Machine": machine, 
            "PM_Duration (hours)": duration / 3600,  # Convert seconds to hours 
            "Makespan (hours)": makespan 
        }) 
    return results 
 
 
# Define PM duration ranges for each machine 
grinder_pm_durations = [2.5 * 3600, 3.0 * 3600, 3.5 * 3600] 
vtd_pm_durations = [1.5 * 3600, 2.0 * 3600, 2.5 * 3600] 
cht_pm_durations = [1.0 * 3600, 1.5 * 3600, 2.0 * 3600] 
 
# Perform sensitivity analysis for each machine 
grinder_results = sensitivity_analysis_pm_duration("Grinder", 
grinder_pm_durations) 
vtd_results = sensitivity_analysis_pm_duration("VTD", vtd_pm_durations) 
cht_results = sensitivity_analysis_pm_duration("CHT", cht_pm_durations) 
 
# Print results 
print("Sensitivity Analysis for PM Duration:") 
for result in grinder_results: 
    print(f"Machine: {result['Machine']}, PM Duration: {result['PM_Duration (hours)']} hours, Makespan: {result['Makespan (hours)']} hours") 
for result in vtd_results: 
    print(f"Machine: {result['Machine']}, PM Duration: {result['PM_Duration (hours)']} hours, Makespan: {result['Makespan (hours)']} hours") 
for result in cht_results: 
    print(f"Machine: {result['Machine']}, PM Duration: {result['PM_Duration (hours)']} hours, Makespan: {result['Makespan (hours)']} hours")