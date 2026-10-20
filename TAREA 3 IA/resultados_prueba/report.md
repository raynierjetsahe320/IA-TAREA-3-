# Reporte experimental

## Introducción

Este informe compara búsqueda sistemática, metaheurísticas y métodos evolutivos en problemas combinatorios y de optimización continua.
- Observaciones: 79
- Combinaciones problema/instancia/algoritmo: 79

## Estrategias y representaciones

- Backtracking con orden de valores menos restrictivo para N-Reinas; cota superior fraccional y orden valor/peso para mochila; coloración DSATUR inicial y búsqueda con filtrado para reducir el número de colores.
- Recocido simulado usa intercambios de columnas para reinas, volteo reparado de bits para mochila, recoloreo de un vértice para grafos y desplazamientos acotados en Eggholder.
- El algoritmo genético usa permutaciones con cruza OX para reinas, vectores binarios reparados para mochila, genes de color por vértice para grafos y coordenadas reales para Eggholder.
- El híbrido transfiere el mejor individuo de GA como estado inicial de SA; se contabilizan ambas fases.

## Diseño experimental

Cada fila conserva semilla, parámetros, factibilidad, tiempo, evaluaciones y procedencia/datos de la instancia. Para instancias estocásticas, se usan semillas reproducibles derivadas de la semilla base y la repetición.

Parámetros configurados:

```json
{"backtracking_node_limit": 10000, "ga": {"crossover_rate": 0.9, "elite_count": 2, "generations": 12, "mutation_rate": 0.05, "population_size": 12, "tournament_size": 3}, "graph_objective": null, "sa": {"cooling_rate": 0.995, "initial_temperature": 100.0, "iterations": 100, "minimum_temperature": 1e-08}}
```

## Datos y limitaciones

- Se usaron las filas de mochila y los generadores de grafos especificados en el cuaderno; `results.csv` registra el origen, las semillas y los datos de cada instancia.
- Las filas de `results.csv` incluyen `instance_source` e `instance_data`; el SHA-256 permite comprobar la identidad de un grafo.
- Una ejecución truncada de backtracking no demuestra ausencia de solución ni optimalidad.
- La desviación estándar resume la variabilidad entre ejecuciones; no equivale a una prueba de significancia.

## Resumen observado

| Problema | Instancia | Algoritmo | Ejecuciones | Mejor objetivo | Objetivo medio | Tiempo medio (s) | Tasa factible | Truncadas |
|---|---|---|---:|---:|---:|---:|---:|---:|
| coloring | n=1000_seed=101 | Backtracking | 1 | 4.0 | 4.0 | 13.4364 | 100.0% | 1 |
| coloring | n=1000_seed=101 | Genetic Algorithm | 1 | 4.0 | 4.0 | 0.3050 | 100.0% | 0 |
| coloring | n=1000_seed=101 | Hybrid GA+SA | 1 | 4.0 | 4.0 | 0.3101 | 100.0% | 0 |
| coloring | n=1000_seed=101 | Simulated Annealing | 1 | 4.0 | 4.0 | 0.2539 | 100.0% | 0 |
| coloring | n=1000_seed=202 | Backtracking | 1 | 4.0 | 4.0 | 16.1438 | 100.0% | 1 |
| coloring | n=1000_seed=202 | Genetic Algorithm | 1 | 4.0 | 4.0 | 0.7377 | 100.0% | 0 |
| coloring | n=1000_seed=202 | Hybrid GA+SA | 1 | 4.0 | 4.0 | 0.7862 | 100.0% | 0 |
| coloring | n=1000_seed=202 | Simulated Annealing | 1 | 4.0 | 4.0 | 0.6193 | 100.0% | 0 |
| coloring | n=1000_seed=303 | Backtracking | 1 | 4.0 | 4.0 | 33.7743 | 100.0% | 1 |
| coloring | n=1000_seed=303 | Genetic Algorithm | 1 | 4.0 | 4.0 | 0.7593 | 100.0% | 0 |
| coloring | n=1000_seed=303 | Hybrid GA+SA | 1 | 4.0 | 4.0 | 0.7830 | 100.0% | 0 |
| coloring | n=1000_seed=303 | Simulated Annealing | 1 | 4.0 | 4.0 | 0.6173 | 100.0% | 0 |
| coloring | n=50_seed=101 | Backtracking | 1 | 4.0 | 4.0 | 0.0010 | 100.0% | 0 |
| coloring | n=50_seed=101 | Genetic Algorithm | 1 | 4.0 | 4.0 | 0.0013 | 100.0% | 0 |
| coloring | n=50_seed=101 | Hybrid GA+SA | 1 | 4.0 | 4.0 | 0.0009 | 100.0% | 0 |
| coloring | n=50_seed=101 | Simulated Annealing | 1 | 4.0 | 4.0 | 0.0009 | 100.0% | 0 |
| coloring | n=50_seed=202 | Backtracking | 1 | 4.0 | 4.0 | 0.0062 | 100.0% | 0 |
| coloring | n=50_seed=202 | Genetic Algorithm | 1 | 4.0 | 4.0 | 0.0041 | 100.0% | 0 |
| coloring | n=50_seed=202 | Hybrid GA+SA | 1 | 4.0 | 4.0 | 0.0048 | 100.0% | 0 |
| coloring | n=50_seed=202 | Simulated Annealing | 1 | 4.0 | 4.0 | 0.0011 | 100.0% | 0 |
| coloring | n=50_seed=303 | Backtracking | 1 | 4.0 | 4.0 | 0.0054 | 100.0% | 0 |
| coloring | n=50_seed=303 | Genetic Algorithm | 1 | 4.0 | 4.0 | 0.0038 | 100.0% | 0 |
| coloring | n=50_seed=303 | Hybrid GA+SA | 1 | 4.0 | 4.0 | 0.0039 | 100.0% | 0 |
| coloring | n=50_seed=303 | Simulated Annealing | 1 | 4.0 | 4.0 | 0.0010 | 100.0% | 0 |
| eggholder | [-512,512]^2 | Genetic Algorithm | 1 | -801.9244705073972 | -801.9244705073972 | 0.0019 | 100.0% | 0 |
| eggholder | [-512,512]^2 | Hybrid GA+SA | 1 | -934.6965082823729 | -934.6965082823729 | 0.0024 | 100.0% | 0 |
| eggholder | [-512,512]^2 | Simulated Annealing | 1 | -557.7385397273783 | -557.7385397273783 | 0.0008 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_0 | Backtracking | 1 | -19.0 | -19.0 | 0.0000 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_0 | Genetic Algorithm | 1 | -19.0 | -19.0 | 0.0015 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_0 | Hybrid GA+SA | 1 | -19.0 | -19.0 | 0.0019 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_0 | Simulated Annealing | 1 | -19.0 | -19.0 | 0.0005 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_1 | Backtracking | 1 | -47.0 | -47.0 | 0.0000 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_1 | Genetic Algorithm | 1 | -47.0 | -47.0 | 0.0015 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_1 | Hybrid GA+SA | 1 | -47.0 | -47.0 | 0.0018 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_1 | Simulated Annealing | 1 | -47.0 | -47.0 | 0.0007 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_2 | Backtracking | 1 | -36.0 | -36.0 | 0.0000 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_2 | Genetic Algorithm | 1 | -36.0 | -36.0 | 0.0013 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_2 | Hybrid GA+SA | 1 | -36.0 | -36.0 | 0.0017 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_2 | Simulated Annealing | 1 | -36.0 | -36.0 | 0.0004 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_3 | Backtracking | 1 | -19.0 | -19.0 | 0.0000 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_3 | Genetic Algorithm | 1 | -19.0 | -19.0 | 0.0014 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_3 | Hybrid GA+SA | 1 | -19.0 | -19.0 | 0.0018 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_3 | Simulated Annealing | 1 | -19.0 | -19.0 | 0.0005 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_4 | Backtracking | 1 | -44.0 | -44.0 | 0.0000 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_4 | Genetic Algorithm | 1 | -43.0 | -43.0 | 0.0012 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_4 | Hybrid GA+SA | 1 | -44.0 | -44.0 | 0.0017 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_4 | Simulated Annealing | 1 | -44.0 | -44.0 | 0.0004 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_5 | Backtracking | 1 | -48.0 | -48.0 | 0.0000 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_5 | Genetic Algorithm | 1 | -48.0 | -48.0 | 0.0014 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_5 | Hybrid GA+SA | 1 | -48.0 | -48.0 | 0.0018 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_5 | Simulated Annealing | 1 | -48.0 | -48.0 | 0.0005 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_6 | Backtracking | 1 | -37.0 | -37.0 | 0.0000 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_6 | Genetic Algorithm | 1 | -37.0 | -37.0 | 0.0012 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_6 | Hybrid GA+SA | 1 | -37.0 | -37.0 | 0.0016 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_6 | Simulated Annealing | 1 | -37.0 | -37.0 | 0.0004 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_7 | Backtracking | 1 | -13.0 | -13.0 | 0.0000 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_7 | Genetic Algorithm | 1 | -13.0 | -13.0 | 0.0013 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_7 | Hybrid GA+SA | 1 | -13.0 | -13.0 | 0.0017 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_7 | Simulated Annealing | 1 | -13.0 | -13.0 | 0.0005 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_8 | Backtracking | 1 | -35.0 | -35.0 | 0.0000 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_8 | Genetic Algorithm | 1 | -35.0 | -35.0 | 0.0013 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_8 | Hybrid GA+SA | 1 | -35.0 | -35.0 | 0.0016 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_8 | Simulated Annealing | 1 | -35.0 | -35.0 | 0.0005 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_9 | Backtracking | 1 | -45.0 | -45.0 | 0.0000 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_9 | Genetic Algorithm | 1 | -45.0 | -45.0 | 0.0013 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_9 | Hybrid GA+SA | 1 | -45.0 | -45.0 | 0.0017 | 100.0% | 0 |
| knapsack | kaggle_opcion1_fila_9 | Simulated Annealing | 1 | -45.0 | -45.0 | 0.0005 | 100.0% | 0 |
| queens | N=100 | Backtracking | 1 | 0.0 | 0.0 | 2.0215 | 100.0% | 0 |
| queens | N=100 | Genetic Algorithm | 1 | 48.0 | 48.0 | 0.0166 | 0.0% | 0 |
| queens | N=100 | Hybrid GA+SA | 1 | 43.0 | 43.0 | 0.0198 | 0.0% | 0 |
| queens | N=100 | Simulated Annealing | 1 | 48.0 | 48.0 | 0.0035 | 0.0% | 0 |
| queens | N=50 | Backtracking | 1 | 0.0 | 0.0 | 0.1780 | 100.0% | 0 |
| queens | N=50 | Genetic Algorithm | 1 | 19.0 | 19.0 | 0.0107 | 0.0% | 0 |
| queens | N=50 | Hybrid GA+SA | 1 | 18.0 | 18.0 | 0.0138 | 0.0% | 0 |
| queens | N=50 | Simulated Annealing | 1 | 28.0 | 28.0 | 0.0035 | 0.0% | 0 |
| queens | N=8 | Backtracking | 1 | 0.0 | 0.0 | 0.0005 | 100.0% | 0 |
| queens | N=8 | Genetic Algorithm | 1 | 1.0 | 1.0 | 0.0019 | 0.0% | 0 |
| queens | N=8 | Hybrid GA+SA | 1 | 1.0 | 1.0 | 0.0025 | 0.0% | 0 |
| queens | N=8 | Simulated Annealing | 1 | 0.0 | 0.0 | 0.0007 | 100.0% | 0 |

## Visualizaciones

Se genera una curva independiente por instancia para evitar mezclar escalas de tamaños diferentes. Las curvas sirven para interpretar convergencia, no como prueba estadística.

## Guía de interpretación

- Para N-Reinas, el objetivo es el número de conflictos. Para coloreado, el objetivo es minimizar el número de colores; `conflicts` registra las aristas en conflicto y la factibilidad exige cero.
- Para mochila, el objetivo se guarda como el negativo del valor total para unificar la minimización; `quality` y `total_value` guardan el valor a maximizar.
- Para Eggholder, un objetivo menor es mejor. Compara mejores valores, distribuciones entre semillas y curvas de convergencia.
- Contrasta calidad con tiempo y evaluaciones. Una tasa factible baja o corridas truncadas requieren una discusión explícita.
- Las curvas muestran promedios de corridas del mismo algoritmo e instancia; no son evidencia estadística por sí solas.

## Conclusiones

Use la tabla y las curvas para contestar qué método obtuvo el mejor objetivo, cuál fue más rápido, qué variabilidad mostró y cómo cambió el resultado con el tamaño. Compruebe el origen y los límites de cada instancia antes de generalizar las conclusiones.
