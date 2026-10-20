import csv
import hashlib
import json
import math
import random
import re
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path


@dataclass(frozen=True)
class KnapsackInstance:
    weights: tuple[float, ...]
    values: tuple[float, ...]
    capacity: float
    source: str = "provided"
    instance_id: str = "knapsack"

    def __post_init__(self) -> None:
        if not self.weights or len(self.weights) != len(self.values):
            raise ValueError("Knapsack weights and values must have the same non-zero length.")
        if not math.isfinite(self.capacity) or self.capacity < 0:
            raise ValueError("Knapsack capacity must be finite and non-negative.")
        if any(not math.isfinite(weight) or weight < 0 for weight in self.weights):
            raise ValueError("Knapsack weights must be finite and non-negative.")
        if any(not math.isfinite(value) or value < 0 for value in self.values):
            raise ValueError("Knapsack values must be finite and non-negative.")


@dataclass(frozen=True)
class GraphInstance:
    adjacency: tuple[frozenset[int], ...]
    source: str
    seed: int | None = None

    @property
    def node_count(self) -> int:
        return len(self.adjacency)

    @cached_property
    def edges(self) -> tuple[tuple[int, int], ...]:
        return tuple(
            (node, neighbor)
            for node, neighbors in enumerate(self.adjacency)
            for neighbor in neighbors
            if node < neighbor
        )


def synthetic_knapsack() -> KnapsackInstance:
    rng = random.Random(314159)
    weights = tuple(rng.randint(2, 30) for _ in range(30))
    values = tuple(rng.randint(5, 80) for _ in range(30))
    return KnapsackInstance(weights, values, sum(weights) // 3, "synthetic seed=314159")


def load_knapsack(path: str | Path) -> KnapsackInstance:
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    return KnapsackInstance(
        tuple(float(value) for value in data["weights"]),
        tuple(float(value) for value in data["values"]),
        float(data["capacity"]),
        f"file: {path}",
    )


_VECTOR_NUMBER = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")
KAGGLE_KNAPSACK_SHA256 = "55b98b9d9d2fc743100f8e48f168e0504b39bee18aad37712d3ccb9d516f044c"


def load_knapsack_instances(path: str | Path, limit: int = 10) -> list[KnapsackInstance]:
    if limit < 1:
        raise ValueError("Knapsack row limit must be at least 1.")
    source_path = Path(path)
    if source_path.suffix.lower() == ".json":
        return [load_knapsack(source_path)]
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    provenance = (
        f"Kaggle warcoder/knapsack-problem; sha256={source_hash}"
        if source_hash == KAGGLE_KNAPSACK_SHA256
        else f"CSV file: {source_path}; sha256={source_hash}"
    )
    with source_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        required = {"Weights", "Prices", "Capacity"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError("Knapsack CSV must contain Weights, Prices, Capacity columns.")
        instances: list[KnapsackInstance] = []
        for row_index, row in enumerate(reader):
            if row_index >= limit:
                break
            weights = _parse_number_vector(row["Weights"], row_index, "Weights")
            values = _parse_number_vector(row["Prices"], row_index, "Prices")
            try:
                capacity = float(row["Capacity"])
            except (TypeError, ValueError) as error:
                raise ValueError(f"Invalid Capacity in CSV row {row_index}.") from error
            instances.append(
                KnapsackInstance(
                    weights,
                    values,
                    capacity,
                    provenance,
                    f"kaggle_opcion1_fila_{row_index}",
                )
            )
    if not instances:
        raise ValueError("Knapsack CSV contains no data rows.")
    return instances


def notebook_graphs() -> list[GraphInstance]:
    """Reproduce the six fixed NetworkX instances from the supplied Colab notebook."""
    try:
        import networkx as nx
    except ImportError as error:
        raise RuntimeError("Generating the supplied graph instances requires networkx.") from error

    graphs: list[GraphInstance] = []
    for node_count in (50, 1000):
        probability = 6 / (node_count - 1)
        for seed in (101, 202, 303):
            graph = nx.fast_gnp_random_graph(
                node_count,
                probability,
                seed=seed,
                directed=False,
            )
            adjacency = [set() for _ in range(node_count)]
            for left, right in graph.edges():
                adjacency[left].add(right)
                adjacency[right].add(left)
            graphs.append(
                GraphInstance(
                    tuple(frozenset(neighbors) for neighbors in adjacency),
                    f"Colab Erdős–Rényi G(n,p); p=6/(n-1); NetworkX {nx.__version__}; seed={seed}",
                    seed,
                )
            )
    return graphs


def load_graph(path: str | Path, node_count: int | None = None) -> GraphInstance:
    edges: list[tuple[int, int]] = []
    largest_node = -1
    for line_number, raw_line in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        fields = line.replace(",", " ").split()
        if len(fields) != 2:
            raise ValueError(f"Invalid edge-list line {line_number}: expected two integer node IDs.")
        try:
            left, right = (int(field) for field in fields)
        except ValueError as error:
            raise ValueError(f"Invalid edge-list line {line_number}: node IDs must be integers.") from error
        if left < 0 or right < 0 or left == right:
            raise ValueError(f"Invalid edge on line {line_number}: IDs must be non-negative and distinct.")
        edges.append((left, right))
        largest_node = max(largest_node, left, right)

    inferred_count = largest_node + 1
    count = inferred_count if node_count is None else node_count
    if count < inferred_count or count < 1:
        raise ValueError("graph-nodes must include all edge IDs and be at least 1.")
    adjacency = [set() for _ in range(count)]
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    return GraphInstance(tuple(frozenset(neighbors) for neighbors in adjacency), str(path))


def _parse_number_vector(value: str, row: int, column: str) -> tuple[float, ...]:
    text = value.strip()
    if not (text.startswith("[") and text.endswith("]")):
        raise ValueError(f"Invalid {column} vector in CSV row {row}.")
    contents = text[1:-1]
    matches = _VECTOR_NUMBER.findall(contents)
    remainder = _VECTOR_NUMBER.sub("", contents).replace(",", "").strip()
    if not matches or remainder:
        raise ValueError(f"Empty {column} vector in CSV row {row}.")
    return tuple(float(number) for number in matches)


def queen_conflicts(solution: tuple[int, ...] | list[int]) -> int:
    descending: dict[int, int] = {}
    ascending: dict[int, int] = {}
    for row, column in enumerate(solution):
        descending[row - column] = descending.get(row - column, 0) + 1
        ascending[row + column] = ascending.get(row + column, 0) + 1
    return sum(count * (count - 1) // 2 for count in descending.values()) + sum(
        count * (count - 1) // 2 for count in ascending.values()
    )


def knapsack_totals(
    solution: tuple[int, ...] | list[int],
    instance: KnapsackInstance,
) -> tuple[float, float]:
    weight = sum(bit * item_weight for bit, item_weight in zip(solution, instance.weights))
    value = sum(bit * item_value for bit, item_value in zip(solution, instance.values))
    return weight, value


def value_density(value: float, weight: float) -> float:
    if weight == 0:
        return math.inf if value > 0 else 0.0
    return value / weight


def graph_conflicts(solution: tuple[int, ...] | list[int], graph: GraphInstance) -> int:
    return sum(solution[left] == solution[right] for left, right in graph.edges)


def eggholder(point: tuple[float, float] | list[float]) -> float:
    x, y = point
    first = -(y + 47) * math.sin(math.sqrt(abs(x / 2 + (y + 47))))
    second = -x * math.sin(math.sqrt(abs(x - (y + 47))))
    return first + second


def validate_coloring(solution: tuple[int, ...] | list[int], graph: GraphInstance, colors: int) -> bool:
    return (
        len(solution) == graph.node_count
        and all(0 <= color < colors for color in solution)
        and graph_conflicts(solution, graph) == 0
    )
