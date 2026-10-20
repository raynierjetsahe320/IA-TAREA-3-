import math
import random
import sys
from collections.abc import Callable
from typing import Any

from .algorithms import genetic_algorithm, simulated_annealing
from .models import GAConfig, SAConfig, SolverResult
from .problems import (
    GraphInstance,
    KnapsackInstance,
    eggholder,
    graph_conflicts,
    knapsack_totals,
    queen_conflicts,
    validate_coloring,
    value_density,
)


def solve_queens_backtracking(size: int, node_limit: int) -> SolverResult:
    if size < 1 or node_limit < 1:
        raise ValueError("N and node_limit must be positive.")
    columns = [-1] * size
    used_columns: set[int] = set()
    used_descending: set[int] = set()
    used_ascending: set[int] = set()
    explored = 0
    solution: tuple[int, ...] | None = None
    limit_reached = False

    def available_columns(row: int) -> list[int]:
        return [
            column
            for column in range(size)
            if column not in used_columns
            and row - column not in used_descending
            and row + column not in used_ascending
        ]

    def search(unassigned_rows: set[int]) -> bool:
        nonlocal explored, solution, limit_reached
        if explored >= node_limit:
            limit_reached = True
            return False
        if not unassigned_rows:
            solution = tuple(columns)
            return True
        domains = {row: available_columns(row) for row in unassigned_rows}
        if any(not domain for domain in domains.values()):
            return False
        row = min(unassigned_rows, key=lambda candidate: (len(domains[candidate]), candidate))
        candidates = domains[row]
        candidates.sort(
            key=lambda column: sum(
                abs(row - other_row) == abs(column - other_column)
                or column == other_column
                for other_row, domain in domains.items()
                if other_row != row
                for other_column in domain
            )
        )
        for column in candidates:
            explored += 1
            columns[row] = column
            used_columns.add(column)
            used_descending.add(row - column)
            used_ascending.add(row + column)
            if search(unassigned_rows - {row}):
                return True
            used_columns.remove(column)
            used_descending.remove(row - column)
            used_ascending.remove(row + column)
            if limit_reached:
                return False
        return False

    found = search(set(range(size)))
    return SolverResult(
        solution,
        0.0 if found else float("inf"),
        explored,
        explored,
        feasible=found,
        limit_reached=limit_reached,
    )


def solve_knapsack_backtracking(instance: KnapsackInstance, node_limit: int) -> SolverResult:
    if node_limit < 1:
        raise ValueError("node_limit must be positive.")
    order = sorted(
        range(len(instance.weights)),
        key=lambda index: value_density(instance.values[index], instance.weights[index]),
        reverse=True,
    )
    best_value = 0
    best_solution = [0] * len(instance.weights)
    current = [0] * len(instance.weights)
    explored = 0
    limit_reached = False

    def fractional_bound(position: int, weight: int, value: int) -> float:
        bound = float(value)
        remaining = instance.capacity - weight
        for item in order[position:]:
            item_weight = instance.weights[item]
            if item_weight == 0:
                bound += instance.values[item]
            elif item_weight <= remaining:
                bound += instance.values[item]
                remaining -= item_weight
            else:
                bound += instance.values[item] * remaining / item_weight
                break
        return bound

    def search(position: int, weight: int, value: int) -> None:
        nonlocal best_value, best_solution, explored, limit_reached
        if explored >= node_limit:
            limit_reached = True
            return
        explored += 1
        if value > best_value:
            best_value = value
            best_solution = current.copy()
        if position == len(order) or fractional_bound(position, weight, value) <= best_value:
            return
        item = order[position]
        if weight + instance.weights[item] <= instance.capacity:
            current[item] = 1
            search(position + 1, weight + instance.weights[item], value + instance.values[item])
            current[item] = 0
        if not limit_reached:
            search(position + 1, weight, value)

    search(0, 0, 0)
    total_weight, total_value = knapsack_totals(best_solution, instance)
    return SolverResult(
        tuple(best_solution),
        -float(total_value),
        explored,
        explored,
        feasible=total_weight <= instance.capacity,
        limit_reached=limit_reached,
    )


def solve_coloring_backtracking(
    graph: GraphInstance,
    colors: int,
    node_limit: int,
) -> SolverResult:
    if colors < 1 or node_limit < 1:
        raise ValueError("colors and node_limit must be positive.")
    assignment = [-1] * graph.node_count
    explored = 0
    limit_reached = False
    solution: tuple[int, ...] | None = None

    def search(colored: int) -> bool:
        nonlocal explored, limit_reached, solution
        if explored >= node_limit:
            limit_reached = True
            return False
        if colored == graph.node_count:
            solution = tuple(assignment)
            return True

        uncolored = [node for node, color in enumerate(assignment) if color < 0]
        node = max(
            uncolored,
            key=lambda candidate: (
                len({assignment[neighbor] for neighbor in graph.adjacency[candidate] if assignment[neighbor] >= 0}),
                len(graph.adjacency[candidate]),
            ),
        )
        forbidden = {assignment[neighbor] for neighbor in graph.adjacency[node] if assignment[neighbor] >= 0}
        options = [color for color in range(colors) if color not in forbidden]
        options.sort(
            key=lambda color: sum(
                color not in {assignment[neighbor] for neighbor in graph.adjacency[other] if assignment[neighbor] >= 0}
                for other in uncolored
                if other != node and other in graph.adjacency[node]
            ),
            reverse=True,
        )
        for color in options:
            explored += 1
            assignment[node] = color
            if all(
                any(color_option not in {
                    assignment[neighbor]
                    for neighbor in graph.adjacency[other]
                    if assignment[neighbor] >= 0
                } for color_option in range(colors))
                for other in uncolored
                if other != node and assignment[other] < 0
            ) and search(colored + 1):
                return True
            assignment[node] = -1
            if limit_reached:
                return False
        return False

    original_recursion_limit = sys.getrecursionlimit()
    required_recursion_limit = graph.node_count + 200
    if required_recursion_limit > original_recursion_limit:
        sys.setrecursionlimit(required_recursion_limit)
    try:
        found = search(0)
    finally:
        if required_recursion_limit > original_recursion_limit:
            sys.setrecursionlimit(original_recursion_limit)
    conflicts = graph_conflicts(solution, graph) if solution is not None else float("inf")
    return SolverResult(
        solution,
        float(conflicts),
        explored,
        explored,
        feasible=found and validate_coloring(solution, graph, colors),
        limit_reached=limit_reached,
    )


def solve_coloring_min_backtracking(graph: GraphInstance, node_limit: int) -> SolverResult:
    if node_limit < 1:
        raise ValueError("node_limit must be positive.")
    best_solution = _greedy_dsatur_coloring(graph)
    best_count = _used_colors(best_solution)
    lower_bound = _greedy_clique_lower_bound(graph)
    evaluations = 0
    limit_reached = False
    history = [float(best_count)]

    for color_count in range(best_count - 1, lower_bound - 1, -1):
        remaining = node_limit - evaluations
        if remaining <= 0:
            limit_reached = True
            break
        candidate = solve_coloring_backtracking(graph, color_count, remaining)
        evaluations += candidate.evaluations
        if candidate.feasible:
            best_solution = candidate.solution
            best_count = _used_colors(best_solution)
            history.append(float(best_count))
            continue
        if candidate.limit_reached:
            limit_reached = True
        break

    return SolverResult(
        best_solution,
        float(best_count),
        evaluations,
        evaluations,
        history,
        feasible=graph_conflicts(best_solution, graph) == 0,
        limit_reached=limit_reached,
        conflicts=graph_conflicts(best_solution, graph),
    )


def coloring_sa_min(
    graph: GraphInstance,
    config: SAConfig,
    rng: random.Random,
) -> SolverResult:
    best_solution = _greedy_dsatur_coloring(graph)
    best_count = _used_colors(best_solution)
    lower_bound = _greedy_clique_lower_bound(graph)
    evaluations = 0
    iterations = 0
    history = [float(best_count)]

    for color_count in range(best_count - 1, lower_bound - 1, -1):
        warm_start = tuple(color % color_count for color in best_solution)
        candidate = coloring_sa(graph, color_count, config, rng, initial_state=warm_start)
        evaluations += candidate.evaluations
        iterations += candidate.iterations
        if not candidate.feasible:
            break
        best_solution = candidate.solution
        best_count = _used_colors(best_solution)
        history.append(float(best_count))

    conflicts = graph_conflicts(best_solution, graph)
    return SolverResult(
        best_solution,
        float(best_count),
        evaluations,
        iterations,
        history,
        feasible=conflicts == 0,
        conflicts=conflicts,
    )


def coloring_ga_min(
    graph: GraphInstance,
    config: GAConfig,
    rng: random.Random,
) -> SolverResult:
    best_solution = _greedy_dsatur_coloring(graph)
    best_count = _used_colors(best_solution)
    lower_bound = _greedy_clique_lower_bound(graph)
    evaluations = 0
    iterations = 0
    history = [float(best_count)]

    for color_count in range(best_count - 1, lower_bound - 1, -1):
        warm_start = tuple(color % color_count for color in best_solution)
        candidate = coloring_ga(
            graph,
            color_count,
            config,
            rng,
            initial_state=warm_start,
        )
        evaluations += candidate.evaluations
        iterations += candidate.iterations
        if not candidate.feasible:
            break
        best_solution = candidate.solution
        best_count = _used_colors(best_solution)
        history.append(float(best_count))

    conflicts = graph_conflicts(best_solution, graph)
    return SolverResult(
        best_solution,
        float(best_count),
        evaluations,
        iterations,
        history,
        feasible=conflicts == 0,
        conflicts=conflicts,
    )


def coloring_hybrid_min(
    graph: GraphInstance,
    sa_config: SAConfig,
    ga_config: GAConfig,
    rng: random.Random,
) -> SolverResult:
    best_solution = _greedy_dsatur_coloring(graph)
    best_count = _used_colors(best_solution)
    lower_bound = _greedy_clique_lower_bound(graph)
    evaluations = 0
    iterations = 0
    history = [float(best_count)]

    for color_count in range(best_count - 1, lower_bound - 1, -1):
        warm_start = tuple(color % color_count for color in best_solution)
        genetic = coloring_ga(
            graph,
            color_count,
            ga_config,
            rng,
            initial_state=warm_start,
        )
        evaluations += genetic.evaluations
        iterations += genetic.iterations
        initial = genetic.solution
        refined = coloring_sa(graph, color_count, sa_config, rng, initial_state=initial)
        evaluations += refined.evaluations
        iterations += refined.iterations
        candidate = refined if refined.objective <= genetic.objective else genetic
        if not candidate.feasible:
            break
        best_solution = candidate.solution
        best_count = _used_colors(best_solution)
        history.append(float(best_count))

    conflicts = graph_conflicts(best_solution, graph)
    return SolverResult(
        best_solution,
        float(best_count),
        evaluations,
        iterations,
        history,
        feasible=conflicts == 0,
        conflicts=conflicts,
    )


def queens_sa(size: int, config: SAConfig, rng: random.Random) -> SolverResult:
    initial = list(range(size))
    rng.shuffle(initial)

    def neighbor(state: tuple[int, ...] | list[int], randomizer: random.Random) -> tuple[int, ...]:
        result = list(state)
        first, second = randomizer.sample(range(size), 2)
        result[first], result[second] = result[second], result[first]
        return tuple(result)

    if size < 2:
        raise ValueError("SA N-Queens requires N >= 2.")
    raw = simulated_annealing(tuple(initial), queen_conflicts, neighbor, config, rng)
    raw.feasible = raw.objective == 0
    return raw


def queens_ga(size: int, config: GAConfig, rng: random.Random) -> SolverResult:
    if size < 1:
        raise ValueError("N must be positive.")
    population = [_random_permutation(size, rng) for _ in range(config.population_size)]

    def crossover(
        first: tuple[int, ...], second: tuple[int, ...], randomizer: random.Random
    ) -> tuple[int, ...]:
        if size < 2:
            return first
        left, right = sorted(randomizer.sample(range(size), 2))
        child: list[int | None] = [None] * size
        child[left:right] = first[left:right]
        remaining = [value for value in second if value not in child]
        cursor = 0
        for index in list(range(right, size)) + list(range(0, left)):
            child[index] = remaining[cursor]
            cursor += 1
        return tuple(int(value) for value in child)

    def mutate(state: tuple[int, ...], randomizer: random.Random) -> tuple[int, ...]:
        result = list(state)
        if randomizer.random() < config.mutation_rate and size > 1:
            first, second = randomizer.sample(range(size), 2)
            result[first], result[second] = result[second], result[first]
        return tuple(result)

    raw = genetic_algorithm(population, queen_conflicts, crossover, mutate, config, rng)
    raw.feasible = raw.objective == 0
    return raw


def knapsack_sa(instance: KnapsackInstance, config: SAConfig, rng: random.Random) -> SolverResult:
    initial = _repair_knapsack(tuple(rng.randrange(2) for _ in instance.weights), instance)

    def objective(state: tuple[int, ...]) -> float:
        return -float(knapsack_totals(state, instance)[1])

    def neighbor(state: tuple[int, ...], randomizer: random.Random) -> tuple[int, ...]:
        index = randomizer.randrange(len(state))
        candidate = list(state)
        candidate[index] = 1 - candidate[index]
        return _repair_knapsack(tuple(candidate), instance)

    result = simulated_annealing(initial, objective, neighbor, config, rng)
    result.feasible = knapsack_totals(result.solution, instance)[0] <= instance.capacity
    return result


def knapsack_ga(instance: KnapsackInstance, config: GAConfig, rng: random.Random) -> SolverResult:
    population = [
        _repair_knapsack(tuple(rng.randrange(2) for _ in instance.weights), instance)
        for _ in range(config.population_size)
    ]

    def objective(state: tuple[int, ...]) -> float:
        return -float(knapsack_totals(state, instance)[1])

    def crossover(first: tuple[int, ...], second: tuple[int, ...], randomizer: random.Random) -> tuple[int, ...]:
        return _repair_knapsack(
            tuple(a if randomizer.random() < 0.5 else b for a, b in zip(first, second)),
            instance,
        )

    def mutate(state: tuple[int, ...], randomizer: random.Random) -> tuple[int, ...]:
        candidate = list(state)
        for index in range(len(candidate)):
            if randomizer.random() < config.mutation_rate:
                candidate[index] = 1 - candidate[index]
        return _repair_knapsack(tuple(candidate), instance)

    result = genetic_algorithm(population, objective, crossover, mutate, config, rng)
    result.feasible = knapsack_totals(result.solution, instance)[0] <= instance.capacity
    return result


def coloring_sa(
    graph: GraphInstance,
    colors: int,
    config: SAConfig,
    rng: random.Random,
    initial_state: tuple[int, ...] | None = None,
) -> SolverResult:
    _validate_color_count(graph, colors)
    if initial_state is not None and (
        len(initial_state) != graph.node_count
        or any(color < 0 or color >= colors for color in initial_state)
    ):
        raise ValueError("SA initial graph coloring must assign a valid color to every node.")
    current = list(
        initial_state
        if initial_state is not None
        else tuple(rng.randrange(colors) for _ in range(graph.node_count))
    )
    current_conflicts = graph_conflicts(current, graph)
    best = current.copy()
    best_conflicts = current_conflicts
    evaluations = 1
    history = [float(best_conflicts)]
    temperature = config.initial_temperature

    for iteration in range(1, config.iterations + 1):
        node = rng.randrange(graph.node_count)
        old_color = current[node]
        new_color = rng.randrange(colors - 1) if colors > 1 else old_color
        if colors > 1 and new_color >= old_color:
            new_color += 1
        old_local_conflicts = sum(
            current[node] == current[neighbor] for neighbor in graph.adjacency[node]
        )
        new_local_conflicts = sum(
            new_color == current[neighbor] for neighbor in graph.adjacency[node]
        )
        candidate_conflicts = current_conflicts - old_local_conflicts + new_local_conflicts
        evaluations += 1
        difference = candidate_conflicts - current_conflicts
        if difference <= 0 or rng.random() < math.exp(-difference / temperature):
            current[node] = new_color
            current_conflicts = candidate_conflicts
        if current_conflicts < best_conflicts:
            best = current.copy()
            best_conflicts = current_conflicts
        history.append(float(best_conflicts))
        temperature = max(config.minimum_temperature, temperature * config.cooling_rate)

    verified_conflicts = graph_conflicts(best, graph)
    if verified_conflicts != best_conflicts:
        raise RuntimeError("Incremental graph-coloring conflict count failed verification.")
    return SolverResult(
        tuple(best),
        float(best_conflicts),
        evaluations,
        config.iterations,
        history,
        feasible=best_conflicts == 0,
        conflicts=best_conflicts,
    )


def coloring_ga(
    graph: GraphInstance,
    colors: int,
    config: GAConfig,
    rng: random.Random,
    initial_state: tuple[int, ...] | None = None,
) -> SolverResult:
    _validate_color_count(graph, colors)
    if initial_state is not None and (
        len(initial_state) != graph.node_count
        or any(color < 0 or color >= colors for color in initial_state)
    ):
        raise ValueError("GA initial graph coloring must assign a valid color to every node.")
    population = [
        tuple(rng.randrange(colors) for _ in range(graph.node_count))
        for _ in range(config.population_size)
    ]
    if initial_state is not None:
        population[0] = initial_state

    def crossover(first: tuple[int, ...], second: tuple[int, ...], randomizer: random.Random) -> tuple[int, ...]:
        return tuple(a if randomizer.random() < 0.5 else b for a, b in zip(first, second))

    def mutate(state: tuple[int, ...], randomizer: random.Random) -> tuple[int, ...]:
        candidate = list(state)
        for node in range(graph.node_count):
            if randomizer.random() < config.mutation_rate:
                candidate[node] = randomizer.randrange(colors)
        return tuple(candidate)

    result = genetic_algorithm(population, lambda state: graph_conflicts(state, graph), crossover, mutate, config, rng)
    result.feasible = validate_coloring(result.solution, graph, colors)
    result.conflicts = int(result.objective)
    return result


def eggholder_sa(config: SAConfig, rng: random.Random) -> SolverResult:
    initial = (rng.uniform(-512, 512), rng.uniform(-512, 512))

    def neighbor(state: tuple[float, float], randomizer: random.Random) -> tuple[float, float]:
        step = max(0.05, 100 * (1 - config.cooling_rate) ** 0.5)
        return tuple(max(-512.0, min(512.0, value + randomizer.gauss(0, step))) for value in state)  # type: ignore[return-value]

    return simulated_annealing(initial, eggholder, neighbor, config, rng)


def eggholder_ga(config: GAConfig, rng: random.Random) -> SolverResult:
    population = [
        (rng.uniform(-512, 512), rng.uniform(-512, 512))
        for _ in range(config.population_size)
    ]

    def crossover(
        first: tuple[float, float], second: tuple[float, float], randomizer: random.Random
    ) -> tuple[float, float]:
        alpha = randomizer.random()
        return tuple(alpha * a + (1 - alpha) * b for a, b in zip(first, second))  # type: ignore[return-value]

    def mutate(state: tuple[float, float], randomizer: random.Random) -> tuple[float, float]:
        if randomizer.random() >= config.mutation_rate:
            return state
        index = randomizer.randrange(2)
        candidate = list(state)
        candidate[index] = max(-512.0, min(512.0, candidate[index] + randomizer.gauss(0, 50)))
        return candidate[0], candidate[1]

    return genetic_algorithm(population, eggholder, crossover, mutate, config, rng)


def hybrid_ga_sa(
    initial_result: SolverResult,
    objective: Callable[[Any], float],
    neighbor: Callable[[Any, random.Random], Any],
    config: SAConfig,
    rng: random.Random,
) -> SolverResult:
    """Refine the GA incumbent with SA, explicitly transferring the best genome."""
    return simulated_annealing(initial_result.solution, objective, neighbor, config, rng)


def _random_permutation(size: int, rng: random.Random) -> tuple[int, ...]:
    values = list(range(size))
    rng.shuffle(values)
    return tuple(values)


def _repair_knapsack(bits: tuple[int, ...], instance: KnapsackInstance) -> tuple[int, ...]:
    repaired = list(bits)
    weight = sum(bit * item_weight for bit, item_weight in zip(repaired, instance.weights))
    while weight > instance.capacity:
        selected = [index for index, bit in enumerate(repaired) if bit]
        least_efficient = min(
            selected,
            key=lambda index: value_density(instance.values[index], instance.weights[index]),
        )
        repaired[least_efficient] = 0
        weight -= instance.weights[least_efficient]
    return tuple(repaired)


def _validate_color_count(graph: GraphInstance, colors: int) -> None:
    if colors < 2 and any(graph.adjacency):
        raise ValueError("At least two colors are required for a graph with edges.")
    if graph.node_count < 1:
        raise ValueError("Graph must contain at least one node.")


def _used_colors(solution: tuple[int, ...]) -> int:
    return len(set(solution))


def _greedy_dsatur_coloring(graph: GraphInstance) -> tuple[int, ...]:
    if graph.node_count < 1:
        raise ValueError("Graph must contain at least one node.")
    assignment = [-1] * graph.node_count
    uncolored = set(range(graph.node_count))
    while uncolored:
        node = max(
            uncolored,
            key=lambda candidate: (
                len({assignment[neighbor] for neighbor in graph.adjacency[candidate] if assignment[neighbor] >= 0}),
                len(graph.adjacency[candidate]),
                -candidate,
            ),
        )
        forbidden = {
            assignment[neighbor]
            for neighbor in graph.adjacency[node]
            if assignment[neighbor] >= 0
        }
        color = 0
        while color in forbidden:
            color += 1
        assignment[node] = color
        uncolored.remove(node)
    return tuple(assignment)


def _greedy_clique_lower_bound(graph: GraphInstance) -> int:
    if not any(graph.adjacency):
        return 1
    best_size = 2
    starts = sorted(range(graph.node_count), key=lambda node: len(graph.adjacency[node]), reverse=True)
    for start in starts[: min(64, graph.node_count)]:
        clique = [start]
        candidates = set(graph.adjacency[start])
        while candidates:
            node = max(candidates, key=lambda candidate: len(graph.adjacency[candidate]))
            clique.append(node)
            candidates.intersection_update(graph.adjacency[node])
        best_size = max(best_size, len(clique))
    return best_size
