import argparse
import sys
from pathlib import Path

from .experiments import print_results_summary, run_experiments, save_outputs, summarize
from .models import GAConfig, SAConfig
from .problems import load_graph, load_knapsack_instances, notebook_graphs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ia-optimizacion",
        description="Compara búsqueda exacta, recocido simulado y algoritmos genéticos.",
    )
    parser.add_argument(
        "--problem",
        choices=("all", "queens", "knapsack", "coloring", "eggholder"),
        default="all",
        help="Familia de problemas a ejecutar (predeterminado: all).",
    )
    parser.add_argument("--runs", type=int, default=None, help="Repeticiones independientes por instancia.")
    parser.add_argument("--seed", type=int, default=2026, help="Semilla base reproducible.")
    parser.add_argument("--output", default="results", help="Carpeta donde se guardan los resultados.")
    parser.add_argument("--quick", action="store_true", help="Presupuesto reducido para verificar el programa.")
    parser.add_argument("--sa-iterations", type=int, default=None, help="Iteraciones máximas de SA.")
    parser.add_argument("--sa-temperature", type=float, default=100.0, help="Temperatura inicial de SA.")
    parser.add_argument("--sa-cooling", type=float, default=0.995, help="Factor geométrico de enfriamiento de SA.")
    parser.add_argument("--ga-population", type=int, default=None, help="Tamaño de población de GA.")
    parser.add_argument("--ga-generations", type=int, default=None, help="Generaciones máximas de GA.")
    parser.add_argument("--ga-crossover", type=float, default=0.9, help="Probabilidad de cruza.")
    parser.add_argument("--ga-mutation", type=float, default=0.05, help="Probabilidad de mutación.")
    parser.add_argument("--ga-elite", type=int, default=None, help="Número de individuos élite.")
    parser.add_argument("--node-limit", type=int, default=None, help="Límite de nodos para backtracking.")
    parser.add_argument(
        "--knapsack-file",
        help="CSV Weights/Prices/Capacity o JSON weights/values/capacity; por defecto usa datos/knapsack_5_items.csv.",
    )
    parser.add_argument(
        "--knapsack-rows",
        type=int,
        default=10,
        help="Primeras filas del CSV de mochila que se ejecutan (predeterminado: 10).",
    )
    parser.add_argument("--graph-file", help="Lista de aristas para una única instancia de grafo.")
    parser.add_argument("--graph-nodes", type=int, help="Número de nodos de la única instancia cargada.")
    parser.add_argument("--graph-50-file", help="Lista de aristas del grafo de 50 nodos.")
    parser.add_argument("--graph-nodes-50", type=int, help="Número explícito de nodos para graph-50-file.")
    parser.add_argument("--graph-1000-file", help="Lista de aristas del grafo de 1000 nodos.")
    parser.add_argument(
        "--graph-nodes-1000",
        type=int,
        help="Número explícito de nodos para graph-1000-file.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.quick:
            runs = args.runs if args.runs is not None else 1
            sa_iterations = args.sa_iterations if args.sa_iterations is not None else 100
            population_size = args.ga_population if args.ga_population is not None else 12
            generations = args.ga_generations if args.ga_generations is not None else 12
            node_limit = args.node_limit if args.node_limit is not None else 10_000
        else:
            runs = args.runs if args.runs is not None else 5
            sa_iterations = args.sa_iterations if args.sa_iterations is not None else 500
            population_size = args.ga_population if args.ga_population is not None else 20
            generations = args.ga_generations if args.ga_generations is not None else 30
            node_limit = args.node_limit if args.node_limit is not None else 2_000
        if runs < 1:
            parser.error("--runs must be at least 1.")

        ga = GAConfig(
            population_size=population_size,
            generations=generations,
            crossover_rate=args.ga_crossover,
            mutation_rate=args.ga_mutation,
            elite_count=args.ga_elite if args.ga_elite is not None else min(2, population_size - 1),
        )
        sa = SAConfig(
            iterations=sa_iterations,
            initial_temperature=args.sa_temperature,
            cooling_rate=args.sa_cooling,
        )
        ga.validate()
        sa.validate()
        if node_limit < 1:
            parser.error("--node-limit must be at least 1.")

        knapsack_path = (
            Path(args.knapsack_file)
            if args.knapsack_file
            else Path(__file__).resolve().parent.parent / "datos" / "knapsack_5_items.csv"
        )
        knapsack = load_knapsack_instances(knapsack_path, args.knapsack_rows)
        graphs = []
        selected_problems = (
            ["queens", "knapsack", "coloring", "eggholder"]
            if args.problem == "all"
            else [args.problem]
        )
        if "coloring" in selected_problems:
            if args.graph_file:
                if args.graph_50_file or args.graph_1000_file:
                    parser.error("--graph-file cannot be combined with graph-50-file/graph-1000-file.")
                graphs = [load_graph(args.graph_file, args.graph_nodes)]
            elif args.graph_50_file or args.graph_1000_file:
                if args.graph_50_file:
                    graphs.append(load_graph(args.graph_50_file, args.graph_nodes_50))
                if args.graph_1000_file:
                    graphs.append(load_graph(args.graph_1000_file, args.graph_nodes_1000))
            else:
                graphs = notebook_graphs()

        print(
            f"Vamos a comparar {runs} repetición(es) por instancia. "
            f"Presupuesto: recocido simulado {sa_iterations} pasos; "
            f"algoritmo genético {population_size} soluciones durante {generations} generaciones; "
            f"búsqueda exacta hasta {node_limit} nodos.",
            flush=True,
        )
        print(
            "Al leer el resumen: factible = respeta las reglas; calidad = qué tan buena "
            "es frente a la mejor solución factible observada. Se reportan por separado.",
            flush=True,
        )
        records = run_experiments(
            selected_problems,
            runs,
            args.seed,
            sa,
            ga,
            node_limit,
            knapsack,
            graphs,
        )
        print("Experimentos completos; guardando CSV, Excel, gráficas y reportes...", flush=True)
        save_outputs(records, args.output)
        print(f"\nListo: se analizaron {len(records)} ejecuciones.")
        print_results_summary(summarize(records))
        print(f"\nArchivos guardados en: {args.output}")
        print("Para explorar los resultados con filtros y curvas, abre report.html en tu navegador.")
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
