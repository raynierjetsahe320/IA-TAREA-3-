import csv
import random
import tempfile
import unittest
import hashlib
from pathlib import Path

import networkx as nx

from ia_optimizacion.algorithms import genetic_algorithm, simulated_annealing
from ia_optimizacion.experiments import run_experiments, save_outputs, summarize
from ia_optimizacion.models import GAConfig, SAConfig
from ia_optimizacion.problems import (
    GraphInstance,
    KnapsackInstance,
    eggholder,
    graph_conflicts,
    load_graph,
    load_knapsack,
    load_knapsack_instances,
    notebook_graphs,
    knapsack_totals,
    queen_conflicts,
    KAGGLE_KNAPSACK_SHA256,
)
from ia_optimizacion.solvers import (
    coloring_ga,
    coloring_sa,
    eggholder_ga,
    eggholder_sa,
    knapsack_ga,
    knapsack_sa,
    queens_ga,
    queens_sa,
    solve_coloring_backtracking,
    solve_coloring_min_backtracking,
    solve_knapsack_backtracking,
    solve_queens_backtracking,
)


class AlgorithmTests(unittest.TestCase):
    def test_n_queens_backtracking_and_metaheuristics(self) -> None:
        result = solve_queens_backtracking(8, 10_000)
        self.assertTrue(result.feasible)
        self.assertEqual(0, queen_conflicts(result.solution))
        for size in (50, 100):
            large = solve_queens_backtracking(size, 100_000)
            self.assertTrue(large.feasible)
            self.assertEqual(0, queen_conflicts(large.solution))
        config = GAConfig(population_size=8, generations=5, elite_count=1)
        self.assertEqual(8, len(queens_ga(8, config, random.Random(3)).solution))
        sa = queens_sa(8, SAConfig(iterations=20), random.Random(2))
        self.assertEqual(8, len(sa.solution))

    def test_knapsack_solvers_respect_capacity(self) -> None:
        instance = KnapsackInstance((2, 3, 4, 5), (4, 5, 7, 9), 7)
        exact = solve_knapsack_backtracking(instance, 1000)
        self.assertTrue(exact.feasible)
        self.assertEqual(13, knapsack_totals(exact.solution, instance)[1])
        zero_weight = KnapsackInstance((0, 2, 3), (5, 4, 5), 2)
        zero_weight_result = solve_knapsack_backtracking(zero_weight, 1000)
        self.assertTrue(zero_weight_result.feasible)
        self.assertEqual(9, knapsack_totals(zero_weight_result.solution, zero_weight)[1])
        config = GAConfig(population_size=8, generations=5, elite_count=1)
        for result in (
            knapsack_sa(instance, SAConfig(iterations=20), random.Random(4)),
            knapsack_ga(instance, config, random.Random(5)),
        ):
            self.assertTrue(result.feasible)
            self.assertLessEqual(knapsack_totals(result.solution, instance)[0], instance.capacity)

    def test_graph_coloring_and_objective(self) -> None:
        graph = GraphInstance(
            (frozenset({1, 2}), frozenset({0, 2}), frozenset({0, 1, 3}), frozenset({2})),
            "test",
        )
        exact = solve_coloring_backtracking(graph, 3, 1000)
        self.assertTrue(exact.feasible)
        self.assertEqual(0, graph_conflicts(exact.solution, graph))
        minimum = solve_coloring_min_backtracking(graph, 1000)
        self.assertTrue(minimum.feasible)
        self.assertEqual(3.0, minimum.objective)
        self.assertEqual(0, minimum.conflicts)
        config = GAConfig(population_size=8, generations=5, elite_count=1)
        self.assertEqual(4, len(coloring_ga(graph, 3, config, random.Random(6)).solution))
        annealed = coloring_sa(graph, 3, SAConfig(iterations=20), random.Random(7))
        self.assertEqual(4, len(annealed.solution))
        self.assertEqual(graph_conflicts(annealed.solution, graph), annealed.conflicts)
        self.assertEqual(float(annealed.conflicts), annealed.objective)

    def test_eggholder_known_point_and_search_bounds(self) -> None:
        self.assertAlmostEqual(-959.6407, eggholder((512, 404.2319)), places=3)
        config = GAConfig(population_size=8, generations=5, elite_count=1)
        for result in (
            eggholder_sa(SAConfig(iterations=20), random.Random(8)),
            eggholder_ga(config, random.Random(9)),
        ):
            self.assertTrue(-512 <= result.solution[0] <= 512)
            self.assertTrue(-512 <= result.solution[1] <= 512)

    def test_generic_algorithms_count_evaluations(self) -> None:
        sa = simulated_annealing(
            10,
            float,
            lambda state, _rng: state - 1,
            SAConfig(iterations=5),
            random.Random(1),
        )
        self.assertEqual(6, sa.evaluations)
        ga = genetic_algorithm(
            [4, 3, 2, 1],
            float,
            lambda a, b, _rng: min(a, b),
            lambda item, _rng: item,
            GAConfig(population_size=4, generations=3, elite_count=1),
            random.Random(2),
        )
        self.assertEqual(16, ga.evaluations)

    def test_experiment_outputs_are_complete(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            records = run_experiments(
                ["queens"],
                1,
                10,
                SAConfig(iterations=3),
                GAConfig(population_size=4, generations=2, elite_count=1),
                1000,
                KnapsackInstance((1,), (1,), 1),
                [],
            )
            self.assertEqual(12, len(records))
            save_outputs(records, temporary)
            self.assertTrue((Path(temporary) / "results.csv").is_file())
            self.assertTrue((Path(temporary) / "summary.csv").is_file())
            self.assertTrue((Path(temporary) / "results.xlsx").is_file())
            self.assertTrue((Path(temporary) / "report.md").is_file())
            self.assertTrue((Path(temporary) / "report.pdf").is_file())
            with (Path(temporary) / "results.csv").open(encoding="utf-8-sig") as results_file:
                result_rows = list(csv.DictReader(results_file))
            self.assertIn("feasibility_status", result_rows[0])
            self.assertIn("quality_status", result_rows[0])
            self.assertNotIn(
                "Pendiente",
                " ".join(row["quality_status"] for row in result_rows),
            )
            dashboard = Path(temporary) / "report.html"
            self.assertTrue(dashboard.is_file())
            dashboard_text = dashboard.read_text(encoding="utf-8")
            self.assertIn("Buscar instancia", dashboard_text)
            self.assertIn("factibilidad y calidad", dashboard_text.lower())
            self.assertIn("temperatura inicial alta", dashboard_text)
            self.assertIn("DSATUR", dashboard_text)
            report_text = (Path(temporary) / "report.md").read_text(encoding="utf-8")
            self.assertIn("Resumen para empezar", report_text)
            self.assertIn("menos conflictos", report_text)
            self.assertIn("no son lo mismo", report_text)
            self.assertIn("Por qué se eligieron estas representaciones", report_text)
            self.assertIn("Por qué estos parámetros", report_text)
            self.assertIn("Cómo interpretar el comportamiento por problema", report_text)

    def test_summary_reports_knapsack_quality_in_user_facing_units(self) -> None:
        records = [
            {
                "problem": "knapsack",
                "instance": "fila 0",
                "algorithm": "Genetic Algorithm",
                "objective": -value,
                "quality": value,
                "time_seconds": 0.1,
                "evaluations": 10,
                "feasible": True,
                "limit_reached": False,
            }
            for value in (4, 8)
        ]
        summary = summarize(records)[0]
        self.assertEqual(6, summary["mean_feasible_quality"])
        self.assertEqual(8, summary["best_feasible_quality"])
        self.assertEqual(8, summary["best_quality"])
        self.assertEqual(0, summary["quality_gap_percent"])
        self.assertIn("Empata", summary["quality_status"])

    def test_feasibility_and_quality_are_reported_independently(self) -> None:
        records = [
            {
                "problem": "knapsack",
                "instance": "fila 0",
                "algorithm": "Backtracking",
                "quality": 10.0,
                "feasible": True,
            },
            {
                "problem": "knapsack",
                "instance": "fila 0",
                "algorithm": "Genetic Algorithm",
                "quality": 5.0,
                "feasible": True,
            },
            {
                "problem": "knapsack",
                "instance": "fila 0",
                "algorithm": "Simulated Annealing",
                "quality": 100.0,
                "feasible": False,
            },
        ]
        from ia_optimizacion.experiments import _annotate_record_quality

        _annotate_record_quality(records)
        self.assertTrue(records[0]["feasibility_status"].startswith("Factible"))
        self.assertEqual(
            "Empata la mejor calidad factible individual observada",
            records[0]["quality_status"],
        )
        self.assertTrue(records[1]["feasibility_status"].startswith("Factible"))
        self.assertIn("50.0%", records[1]["quality_status"])
        self.assertTrue(records[2]["feasibility_status"].startswith("No factible"))
        self.assertEqual("", records[2]["quality_gap_percent"])
        self.assertIn("no comparable", records[2]["quality_status"])

    def test_summary_quality_gap_compares_only_feasible_means(self) -> None:
        records = []
        for algorithm, quality, feasible in (
            ("Backtracking", 10.0, True),
            ("Genetic Algorithm", 5.0, True),
            ("Simulated Annealing", 100.0, False),
        ):
            records.append(
                {
                    "problem": "knapsack",
                    "instance": "fila 0",
                    "algorithm": algorithm,
                    "objective": -quality,
                    "quality": quality,
                    "time_seconds": 0.1,
                    "evaluations": 10,
                    "feasible": feasible,
                    "limit_reached": False,
                }
            )
        summaries = summarize(records)
        by_algorithm = {row["algorithm"]: row for row in summaries}
        self.assertEqual(0, by_algorithm["Backtracking"]["quality_gap_percent"])
        self.assertEqual(50, by_algorithm["Genetic Algorithm"]["quality_gap_percent"])
        self.assertEqual("", by_algorithm["Simulated Annealing"]["quality_gap_percent"])
        self.assertIn("Sin solución factible", by_algorithm["Simulated Annealing"]["quality_status"])

    def test_external_instance_loaders(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            knapsack_path = directory / "knapsack.json"
            knapsack_path.write_text(
                '{"weights":[2,3],"values":[4,5],"capacity":3}',
                encoding="utf-8-sig",
            )
            graph_path = directory / "graph.txt"
            graph_path.write_text("0 1\n1 2\n", encoding="utf-8-sig")
            knapsack = load_knapsack(knapsack_path)
            csv_path = directory / "knapsack.csv"
            csv_path.write_text(
                "Weights,Prices,Capacity,Best picks,Best price\n"
                "\"[2 3]\",\"[4 5]\",3,\"[0 1]\",5\n",
                encoding="utf-8-sig",
            )
            instances = load_knapsack_instances(csv_path)
            graph = load_graph(graph_path, node_count=4)
            self.assertEqual(3, knapsack.capacity)
            self.assertEqual("kaggle_opcion1_fila_0", instances[0].instance_id)
            self.assertEqual((2.0, 3.0), instances[0].weights)
            self.assertEqual(4, graph.node_count)
            self.assertEqual(frozenset(), graph.adjacency[3])

    def test_notebook_graph_instances_match_sizes_and_seeds(self) -> None:
        graphs = notebook_graphs()
        self.assertEqual(
            [(50, 101), (50, 202), (50, 303), (1000, 101), (1000, 202), (1000, 303)],
            [(graph.node_count, graph.seed) for graph in graphs],
        )
        for graph in graphs:
            expected = nx.fast_gnp_random_graph(
                graph.node_count,
                6 / (graph.node_count - 1),
                seed=graph.seed,
                directed=False,
            )
            actual_edges = {
                (node, neighbor)
                for node, neighbors in enumerate(graph.adjacency)
                for neighbor in neighbors
                if node < neighbor
            }
            self.assertEqual(set(expected.edges()), actual_edges)

    def test_bundled_kaggle_knapsack_dataset_hash_and_selected_rows(self) -> None:
        dataset_path = Path(__file__).parents[1] / "datos" / "knapsack_5_items.csv"
        self.assertEqual(KAGGLE_KNAPSACK_SHA256, hashlib.sha256(dataset_path.read_bytes()).hexdigest())
        instances = load_knapsack_instances(dataset_path)
        self.assertEqual(10, len(instances))
        self.assertEqual("kaggle_opcion1_fila_0", instances[0].instance_id)
        self.assertEqual((46.0, 40.0, 42.0, 38.0, 10.0), instances[0].weights)
        self.assertEqual((12.0, 19.0, 19.0, 15.0, 8.0), instances[0].values)
        self.assertEqual(40.0, instances[0].capacity)


if __name__ == "__main__":
    unittest.main()
