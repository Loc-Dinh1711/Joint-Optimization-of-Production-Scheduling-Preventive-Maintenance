# Genetic Algorithm code
import random
# Parameters 
POP_SIZE = 100 
GEN_LIMIT = 1000 
CROSSOVER_RATE = 0.8 
MUTATION_RATE = 0.2 
 
# Problem-specific parameters 
num_panels = 15294  # Total number of panels 
machines = ["Grinder", "VTD", "CHT"]  # Machines in sequence 
processing_time = {  # Processing times in seconds 
    "Grinder": 18.00, 
    "VTD": 18.79, 
    "CHT": 34.95 
} 
 
# Baseline PM times from MILP (in hours) 
milp_pm_times = { 
    "Grinder": 158.50, 
    "VTD": 159.50, 
    "CHT": 160.00 
} 
 
# Convert PM times to seconds for calculation 
milp_pm_times_sec = {m: t * 3600 for m, t in milp_pm_times.items()} 
 
# Helper functions 
def initialize_population(milp_solution, pop_size): 
    """Initialize population using MILP result.""" 
    population = [] 
    for _ in range(pop_size): 
        chromosome = milp_solution.copy() 
        random.shuffle(chromosome)  # Add diversity 
        population.append(chromosome) 
    return population 
 
def calculate_makespan_and_pm(chromosome): 
    """Calculate makespan and PM times based on the chromosome.""" 
    completion_time = {m: 0 for m in machines} 
    pm_times = {m: 0 for m in machines} 
    pm_done = {m: False for m in machines}  # Track if PM has been scheduled 
 
    for operation in chromosome: 
        machine = operation[1] 
        processing = processing_time[machine] 
 
        # Add PM if not done yet and time exceeds baseline 
        if not pm_done[machine] and completion_time[machine] >= milp_pm_times_sec[machine]: 
            completion_time[machine] += 3600  # Assume PM takes 1 hour 
            pm_done[machine] = True 
            pm_times[machine] = completion_time[machine] / 3600  # Convert to hours 
 
        # Update the machine's completion time 
        completion_time[machine] += processing 
 
    # If PM is not done by the end, schedule it at the last moment 
    for machine in machines: 
        if not pm_done[machine]: 
            completion_time[machine] += 3600 
            pm_done[machine] = True 
            pm_times[machine] = completion_time[machine] / 3600  # Convert to hours 
 
    return max(completion_time.values()), pm_times 
 
def selection(population, fitness): 
    """Select parents using highest throughput mechanism.""" 
    sorted_population = [x for _, x in sorted(zip(fitness, population))] 
    return sorted_population[:2]  # Return two best chromosomes 
 
def crossover(parent1, parent2): 
    """Perform multi-point crossover.""" 
    point = random.randint(1, len(parent1) - 2) 
    child1 = parent1[:point] + parent2[point:] 
    child2 = parent2[:point] + parent1[point:] 
    return child1, child2 
 
def mutate(chromosome): 
    """Perform mutation by swapping two random operations.""" 
    if random.random() < MUTATION_RATE: 
        i, j = random.sample(range(len(chromosome)), 2) 
        chromosome[i], chromosome[j] = chromosome[j], chromosome[i] 
 
def genetic_algorithm(milp_solution): 
    """Main Genetic Algorithm loop.""" 
    population = initialize_population(milp_solution, POP_SIZE) 
    best_solution = None 
    best_makespan = float('inf') 
    best_pm_times = None 
 
    for generation in range(GEN_LIMIT): 
        # Evaluate fitness 
        fitness = [] 
        makespan_and_pm = [] 
        for chromosome in population: 
            makespan, pm_times = calculate_makespan_and_pm(chromosome) 
            fitness.append(makespan) 
            makespan_and_pm.append((makespan, pm_times)) 
 
        # Update best solution 
        for i, (makespan, pm_times) in enumerate(makespan_and_pm): 
            if makespan < best_makespan: 
                best_makespan = makespan 
                best_solution = population[i] 
                best_pm_times = pm_times 
 
        # Selection 
        parents = selection(population, fitness) 
 
        # Crossover and mutation 
        new_population = [] 
        while len(new_population) < POP_SIZE: 
            if random.random() < CROSSOVER_RATE: 
                child1, child2 = crossover(parents[0], parents[1]) 
                mutate(child1) 
                mutate(child2) 
                new_population.extend([child1, child2]) 
            else: 
                new_population.extend(parents) 
 
        # Replace old population 
        population = new_population[:POP_SIZE] 
 
        # Termination check 
        if generation % 100 == 0: 
            print(f"Generation {generation}: Best Makespan = {best_makespan / 3600:.2f} hours") 
 
    return best_solution, best_makespan, best_pm_times 
 
# Example MILP solution (to be replaced with actual MILP result) 
milp_solution = [(i, m) for i in range(1, num_panels + 1) for m in machines] 
 
# Run Genetic Algorithm 
best_solution, best_makespan, best_pm_times = genetic_algorithm(milp_solution) 
 
# Output results 
print(f"Best Makespan: {best_makespan / 3600:.2f} hours") 
print("PM Times (hours):") 
for machine, pm_time in best_pm_times.items(): 
    print(f"  {machine}: {pm_time:.2f} hours")