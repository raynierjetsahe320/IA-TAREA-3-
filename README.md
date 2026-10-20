# Tarea 3: búsqueda y optimización

Proyecto reproducible en Python para comparar backtracking con filtrado, recocido
simulado (SA), algoritmo genético (GA) y un híbrido GA+SA en N-Reinas, Mochila
0/1 y coloreado de grafos. SA y GA también se aplican a la función Eggholder.

## Requisitos

- Python 3.10 o posterior
- Dependencias de visualización y Excel, instaladas con
  `pip install -r requirements.txt`

## Ejecución rápida

### Windows (PowerShell)

```powershell
cd "C:\ruta\al\proyecto"
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ia_optimizacion --quick --output resultados
```

Usa la ruta real de la carpeta del proyecto en el comando `cd`. Por ejemplo:
`cd "C:\Users\rayni\OneDrive\Datos adjuntos\Desktop\TAREA 3 IA"`.

No es necesario activar el entorno virtual: ejecutar directamente
`.\.venv\Scripts\python.exe` evita depender de que Python esté agregado al PATH
y de las políticas de PowerShell que pueden bloquear `Activate.ps1`. Si `py -3`
no se reconoce, instala Python 3.10 o posterior desde python.org y vuelve a
ejecutar los comandos.

### Linux o macOS

Desde la raíz del proyecto:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m ia_optimizacion --quick --output resultados
```

La ejecución completa, con cinco repeticiones independientes por instancia, es:

```powershell
.\.venv\Scripts\python.exe -m ia_optimizacion --runs 5 --seed 2026 --output resultados
```

En Linux o macOS, reemplaza el ejecutable por `./.venv/bin/python`:

```bash
./.venv/bin/python -m ia_optimizacion --runs 5 --seed 2026 --output resultados
```

Se puede ejecutar solo una familia de problemas:

```powershell
.\.venv\Scripts\python.exe -m ia_optimizacion --problem queens --runs 5
.\.venv\Scripts\python.exe -m ia_optimizacion --problem knapsack
.\.venv\Scripts\python.exe -m ia_optimizacion --problem coloring --graph-file datos\grafo.txt --graph-nodes 50
.\.venv\Scripts\python.exe -m ia_optimizacion --problem eggholder --runs 20
```

En Linux o macOS, usa `./.venv/bin/python` en lugar de
`.\.venv\Scripts\python.exe`. El comando
`.\.venv\Scripts\python.exe -m ia_optimizacion --help` muestra todos los
parámetros en Windows.
Las primeras diez filas de mochila se usan por defecto, igual que en el
cuaderno. Puedes cambiar la cantidad con `--knapsack-rows`.

## Instancias

Las instancias del cuaderno adjunto se integraron al proyecto:

- [knapsack_5_items.csv](datos/knapsack_5_items.csv): el CSV `knapsack_5_items.csv`
  del [conjunto público `warcoder/knapsack-problem`](https://www.kaggle.com/datasets/warcoder/knapsack-problem).
  El archivo descargado se verificó contra el SHA-256 indicado en el cuaderno.
  Se toman las filas 0–9, respetando el orden y sin usar `Best picks` ni
  `Best price`.
- Seis grafos Erdős–Rényi de NetworkX, con 50 y 1000 nodos, tres semillas por
  tamaño (101, 202, 303) y `p = 6/(n-1)`, como en el cuaderno. Se vuelven a
  generar de forma determinista; cada registro guarda semilla y hash de aristas.
- N-Reinas con N = 8, 50 y 100.

La mochila se carga por defecto desde el CSV incluido. También puedes cargar
un CSV compatible con columnas `Weights`, `Prices`, `Capacity` o un JSON con:

```json
{
  "weights": [2, 3, 4],
  "values": [4, 5, 7],
  "capacity": 5
}
```

Para reemplazar los grafos generados por un archivo propio, se puede usar una
lista de aristas, una pareja de IDs enteros base cero por línea:
`--graph-file datos\grafo.txt --graph-nodes 50`. Se aceptan líneas vacías,
comentarios `#` y vértices aislados mediante `--graph-nodes`.

## Algoritmos y evaluación

- **Backtracking:** N-Reinas usa dominios de columnas válidas, propagación de
  restricciones y orden de valores menos restrictivo; mochila usa orden por
  razón valor/peso y cota superior fraccional; coloreado usa DSATUR y filtrado
  de dominios, empezando por una coloración DSATUR factible y probando menos
  colores hasta certificar el límite o alcanzar el presupuesto.
- **SA:** acepta mejoras y, con probabilidad dependiente de la temperatura,
  algunos empeoramientos para escapar de óptimos locales. El enfriamiento y el
  presupuesto de iteraciones son configurables.
- **GA:** torneo, cruza, mutación y elitismo. La representación se adapta a cada
  problema: permutación para reinas, vector binario para mochila, colores por
  vértice para grafos y dos coordenadas reales para Eggholder.
- **Híbrido (extra):** GA propone asignaciones para un número de colores menor
  que la incumbente y SA refina esa misma asignación antes de pasar a probar
  menos colores.

Las ejecuciones estocásticas reciben semillas derivadas de la semilla base y
del número de repetición. Los algoritmos comparan cada método sobre la misma
instancia. El programa muestra el avance después de cada problema, instancia y
repetición. Los valores predeterminados son SA: 500 iteraciones; GA: población
20 por 30 generaciones; y backtracking: 2,000 nodos. Se pueden aumentar con los
parámetros de la CLI. Backtracking para grafos grandes tiene un límite de
nodos; un resultado con `limit_reached=true` se debe interpretar como búsqueda
truncada, no como prueba de que el grafo no tiene solución.

## Resultados generados

La carpeta de salida contiene:

- `results.csv`: observaciones individuales, semillas, parámetros, tiempos,
  evaluaciones, factibilidad y mejor solución.
- `summary.csv`: medias, desviación estándar y resultados factibles por combinación.
- `results.xlsx`: hojas `Results` y `Summary`; `mean_feasible_quality` expresa el
  promedio en la unidad que una persona reconoce (por ejemplo, valor de mochila
  o cantidad de colores), no el objetivo interno del algoritmo.
- Los datos distinguen `feasibility_status` (si la solución respeta las reglas)
  de `quality_status` (cómo se compara su calidad con la mejor solución factible
  observada en esa instancia). `quality_gap_percent` expresa esa diferencia.
  En `summary.csv`, la brecha compara promedios factibles de cada método; en
  `results.csv`, compara cada corrida con la mejor solución factible individual
  observada. No implica optimalidad probada.
- `convergence_<problem>_<instance>.png`: curvas de convergencia por método e instancia.
- `report.html`: tablero interactivo que funciona sin internet. Permite filtrar
  por problema y método, buscar instancias, comparar el mejor promedio factible
  y el método más rápido, y desplegar las curvas de avance.
- `report.md`: explicación en lenguaje sencillo de qué se mide, qué método
  destacó y cómo interpretar los límites de la búsqueda, las representaciones
  elegidas, los presupuestos y el comportamiento esperado por problema.
- `report.pdf`: reporte con esas explicaciones, la distinción factibilidad /
  calidad y tablas de resultados.

Al terminar, la consola también muestra un resumen por instancia. «Mejor
promedio factible» compara únicamente corridas con soluciones válidas. El
objetivo cambia según el problema: en mochila se busca más valor; en reinas,
menos conflictos; en coloreado, menos colores; y en Eggholder, un valor menor.
Una búsqueda exacta truncada no demuestra que la solución encontrada sea óptima.
Abre `report.html` en Edge, Chrome o Firefox para explorar los resultados.

### Cómo distinguir factibilidad de calidad

- **Factible** significa que se cumplen las reglas: capacidad de la mochila,
  cero ataques entre reinas, cero conflictos entre vértices coloreados o
  coordenadas dentro del dominio de Eggholder.
- **Calidad** mide qué tan conveniente es una solución *entre las factibles*.
  Una mochila puede respetar la capacidad y aun así obtener poco valor; un
  coloreado válido puede usar más colores de los necesarios.
- La brecha se calcula frente a la mejor calidad factible observada en la misma
  instancia. Es una comparación empírica entre métodos, no una afirmación de
  optimalidad. En N-Reinas, todas las soluciones factibles empatan con cero
  conflictos.
- La explicación del reporte describe por qué la representación, los operadores
  y los presupuestos pueden producir comportamientos distintos. Contrasta esas
  razones con los tiempos, la calidad, la tasa factible y los truncamientos
  observados; no son garantías de que un algoritmo siempre se comporte igual.

Los resultados no incorporan conclusiones predeterminadas: las conclusiones
deben basarse en los archivos de cada ejecución y distinguir calidad, tiempo,
factibilidad y truncamiento.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```# IA-TAREA-3-
