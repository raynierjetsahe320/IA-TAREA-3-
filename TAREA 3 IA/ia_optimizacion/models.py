from dataclasses import dataclass, field
from typing import Any


@dataclass
class SolverResult:
    solution: Any
    objective: float
    evaluations: int
    iterations: int
    convergence: list[float] = field(default_factory=list)
    feasible: bool = True
    limit_reached: bool = False
    conflicts: int | None = None


@dataclass(frozen=True)
class SAConfig:
    iterations: int = 2000
    initial_temperature: float = 100.0
    cooling_rate: float = 0.995
    minimum_temperature: float = 1e-8

    def validate(self) -> None:
        if self.iterations < 1:
            raise ValueError("SA iterations must be at least 1.")
        if self.initial_temperature <= 0:
            raise ValueError("SA initial_temperature must be positive.")
        if not 0 < self.cooling_rate < 1:
            raise ValueError("SA cooling_rate must be between 0 and 1.")
        if self.minimum_temperature <= 0:
            raise ValueError("SA minimum_temperature must be positive.")


@dataclass(frozen=True)
class GAConfig:
    population_size: int = 40
    generations: int = 80
    crossover_rate: float = 0.9
    mutation_rate: float = 0.05
    elite_count: int = 2
    tournament_size: int = 3

    def validate(self) -> None:
        if self.population_size < 2:
            raise ValueError("GA population_size must be at least 2.")
        if self.generations < 1:
            raise ValueError("GA generations must be at least 1.")
        if not 0 <= self.crossover_rate <= 1:
            raise ValueError("GA crossover_rate must be between 0 and 1.")
        if not 0 <= self.mutation_rate <= 1:
            raise ValueError("GA mutation_rate must be between 0 and 1.")
        if not 1 <= self.elite_count < self.population_size:
            raise ValueError("GA elite_count must be between 1 and population_size - 1.")
        if not 1 <= self.tournament_size <= self.population_size:
            raise ValueError("GA tournament_size must be between 1 and population_size.")


def result_parameters(sa: SAConfig, ga: GAConfig, node_limit: int) -> dict[str, Any]:
    return {
        "sa": {
            "iterations": sa.iterations,
            "initial_temperature": sa.initial_temperature,
            "cooling_rate": sa.cooling_rate,
            "minimum_temperature": sa.minimum_temperature,
        },
        "ga": {
            "population_size": ga.population_size,
            "generations": ga.generations,
            "crossover_rate": ga.crossover_rate,
            "mutation_rate": ga.mutation_rate,
            "elite_count": ga.elite_count,
            "tournament_size": ga.tournament_size,
        },
        "backtracking_node_limit": node_limit,
    }
