import math
import random
from collections.abc import Callable, Sequence
from typing import TypeVar

from .models import GAConfig, SAConfig, SolverResult

Genome = TypeVar("Genome")


def simulated_annealing(
    initial: Genome,
    objective: Callable[[Genome], float],
    neighbor: Callable[[Genome, random.Random], Genome],
    config: SAConfig,
    rng: random.Random,
) -> SolverResult:
    config.validate()
    current = initial
    current_score = objective(current)
    evaluations = 1
    best = current
    best_score = current_score
    history = [best_score]
    temperature = config.initial_temperature
    steps = 0

    for steps in range(1, config.iterations + 1):
        candidate = neighbor(current, rng)
        candidate_score = objective(candidate)
        evaluations += 1
        difference = candidate_score - current_score
        if difference <= 0 or rng.random() < math.exp(-difference / temperature):
            current, current_score = candidate, candidate_score
        if current_score < best_score:
            best, best_score = current, current_score
        history.append(best_score)
        temperature = max(config.minimum_temperature, temperature * config.cooling_rate)

    return SolverResult(best, best_score, evaluations, steps, history)


def genetic_algorithm(
    initial_population: Sequence[Genome],
    objective: Callable[[Genome], float],
    crossover: Callable[[Genome, Genome, random.Random], Genome],
    mutate: Callable[[Genome, random.Random], Genome],
    config: GAConfig,
    rng: random.Random,
) -> SolverResult:
    config.validate()
    if len(initial_population) != config.population_size:
        raise ValueError("Initial population size must match GA population_size.")

    population = list(initial_population)
    scores = [objective(individual) for individual in population]
    evaluations = len(population)
    best_index = min(range(len(population)), key=scores.__getitem__)
    best = population[best_index]
    best_score = scores[best_index]
    history = [best_score]

    for _ in range(config.generations):
        ranked = sorted(range(len(population)), key=scores.__getitem__)
        next_population = [population[index] for index in ranked[: config.elite_count]]
        while len(next_population) < config.population_size:
            parent_a = _tournament(population, scores, config.tournament_size, rng)
            parent_b = _tournament(population, scores, config.tournament_size, rng)
            child = (
                crossover(parent_a, parent_b, rng)
                if rng.random() < config.crossover_rate
                else parent_a
            )
            next_population.append(mutate(child, rng))

        population = next_population
        scores = [objective(individual) for individual in population]
        evaluations += len(population)
        generation_best = min(range(len(population)), key=scores.__getitem__)
        if scores[generation_best] < best_score:
            best = population[generation_best]
            best_score = scores[generation_best]
        history.append(best_score)

    return SolverResult(best, best_score, evaluations, config.generations, history)


def _tournament(
    population: Sequence[Genome],
    scores: Sequence[float],
    size: int,
    rng: random.Random,
) -> Genome:
    contestants = rng.sample(range(len(population)), size)
    winner = min(contestants, key=scores.__getitem__)
    return population[winner]
