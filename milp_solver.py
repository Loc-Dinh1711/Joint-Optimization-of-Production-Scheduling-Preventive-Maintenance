# MILP code
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
T_PM = pulp.LpVariable.dicts("PM_Start_Time", machines, lowBound=0, 
cat="Continuous")  # Start time of PM 
 
# Objective: Minimize makespan 
model += C_max, "Minimize_Makespan" 
 
# Constraints 
for i in range(1, panels_per_week + 1): 
    for m_idx, m in enumerate(machines): 
        if m_idx == 0:  # First machine (Grinder) 
            # Start time for the first machine 
            model += C[(i, m)] >= (i - 1) * processing_time[m], f"Start_Grinder_Panel_{i}" 
        else: 
            # Sequence constraint: Operation must wait for the previous machine to complete 
            prev_machine = machines[m_idx - 1] 
            model += C[(i, m)] >= C[(i, prev_machine)] + processing_time[m], f"Sequence_{m}_Panel_{i}" 
 
        # Ensure that the current panel finishes processing before the next one starts 
        if i > 1: 
            model += C[(i, m)] >= C[(i - 1, m)] + processing_time[m], f"No_Overlap_{m}_Panel_{i}" 
 
# Makespan constraint: C_max must be greater than or equal to the completion of the last panel on the last machine 
for i in range(1, panels_per_week + 1): 
    model += C_max >= C[(i, "CHT")], f"Makespan_Panel_{i}" 
 
# PM constraints 
for m in machines: 
    # Each machine undergoes 1 PM per week 
    model += Y[m] == 1, f"PM_Frequency_{m}" 
 
    # PM must occur during available time 
    model += T_PM[m] + pm_duration[m] <= net_available_time, f"PM_Availability_{m}" 
 
    # PM cannot overlap with production 
    for i in range(1, panels_per_week + 1): 
        model += T_PM[m] >= C[(i, m)] + processing_time[m], f"PM_Start_After_Production_{m}_Panel_{i}" 
 
# Solve the model 
solver = pulp.PULP_CBC_CMD() 
model.solve(solver) 
 
# Output results 
if pulp.LpStatus[model.status] == "Optimal": 
    print(f"Optimal Makespan: {pulp.value(C_max) / 3600:.2f} hours") 
    for i in range(1, panels_per_week + 1): 
        for m in machines: 
            print(f"Panel {i}, {m}: Completion Time = {pulp.value(C[(i, m)]) / 3600:.2f} hours") 
    for m in machines: 
        print(f"Machine {m}: PM Scheduled = {pulp.value(Y[m])}, PM Start Time = {pulp.value(T_PM[m]) / 3600:.2f} hours") 
else: 
    print("No optimal solution found.")

