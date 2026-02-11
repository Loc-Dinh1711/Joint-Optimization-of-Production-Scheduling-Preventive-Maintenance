# Sensitivity analysis of MILP for Processing time
import pulp 
 
# Constants 
panels_per_week = 15294  # Weekly production target 
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
 
# Function to build and solve the MILP model 
def build_and_solve_milp(panels_per_week, processing_time, pm_duration): 
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
 
# Perform sensitivity analysis for all machines 
def sensitivity_analysis_all_machines(parameter_name, parameter_values): 
    global panels_per_week  # Declare panels_per_week as global 
 
    original_makespan = build_and_solve_milp(panels_per_week, processing_time, pm_duration) 
    results = [] 
 
    for value in parameter_values: 
        if parameter_name == "Grinder_Processing_Time": 
            processing_time["Grinder"] = value 
        elif parameter_name == "VTD_Processing_Time": 
            processing_time["VTD"] = value 
        elif parameter_name == "CHT_Processing_Time": 
            processing_time["CHT"] = value 
        elif parameter_name == "Production_Target": 
            panels_per_week = int(value)  # Update the global variable 
 
        # Solve the MILP model with the updated parameter 
        new_makespan = build_and_solve_milp(panels_per_week, processing_time, pm_duration) 
 
        # Calculate deviation from the original makespan 
        deviation = None 
        if new_makespan is not None and original_makespan is not None: 
            deviation = (new_makespan - original_makespan) / original_makespan * 100 
 
        # Store results 
        results.append({ 
            "Machine": parameter_name.split("_")[0], 
            "Parameter_Value": value, 
            "New_Makespan": new_makespan, 
            "Deviation (%)": deviation 
        }) 
 
    return results 
 
# Define ranges for each machine's processing time 
grinder_values = [15.0, 16.0, 17.0, 18.0, 19.0, 20.0]  # Seconds 
vtd_values = [16.0, 17.0, 18.0, 19.0, 20.0, 21.0]  # Seconds 
cht_values = [30.0, 32.0, 34.0, 36.0, 38.0, 40.0]  # Seconds 
 
# Perform sensitivity analysis for Grinder 
grinder_results = sensitivity_analysis_all_machines("Grinder_Processing_Time", grinder_values) 
 
# Perform sensitivity analysis for VTD 
vtd_results = sensitivity_analysis_all_machines("VTD_Processing_Time", vtd_values) 
 
# Perform sensitivity analysis for CHT 
cht_results = sensitivity_analysis_all_machines("CHT_Processing_Time", cht_values) 
 
# Combine and print results 
print(f"Sensitivity Analysis for Grinder Processing Time:") 
for result in grinder_results: 
    print(f"Machine: {result['Machine']}, Parameter Value: {result['Parameter_Value']}, New Makespan: {result['New_Makespan']}, Deviation (%): {result['Deviation (%)']}") 
 
print(f"\nSensitivity Analysis for VTD Processing Time:") 
for result in vtd_results: 
    print(f"Machine: {result['Machine']}, Parameter Value: {result['Parameter_Value']}, New Makespan: {result['New_Makespan']}, Deviation (%): {result['Deviation (%)']}") 
 
print(f"\nSensitivity Analysis for CHT Processing Time:") 
for result in cht_results: 
    print(f"Machine: {result['Machine']}, Parameter Value: {result['Parameter_Value']}, New Makespan: {result['New_Makespan']}, Deviation (%): {result['Deviation (%)']}") 