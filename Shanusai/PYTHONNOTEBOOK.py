"""
# Smart Waste Collection Agent - IDA* Algorithm
**Assignment 1 – PS1**

---

## Problem

We have a Smart Waste Collection Robot operating in Bengaluru city. The city's road network is represented as a weighted graph — nodes are waste collection centers / processing plants, and edges are roads with associated travel costs.

The robot needs to find the **cheapest route** from a given source to a destination. Since it runs on limited battery, we want to minimize the total travel cost.

We'll use **IDA*** (Iterative Deepening A*) to solve this.

---

## 1. PEAS Analysis

| Component | Description |
|-----------|-------------|
| **Performance** | Minimize total travel cost from source to destination; find the optimal (cheapest) path |
| **Environment** | Weighted undirected graph — static, fully observable, deterministic. Nodes are locations, edges are roads with costs |
| **Actuators** | Move along a road from current node to a neighboring node |
| **Sensors** | Knows current location, connected roads + their weights, and where the goal is |

**Agent type**: Goal-based, operating in a fully observable, deterministic, static, discrete environment.

## 2. Heuristic — Explanation and Justification

I'm using a **hop-count based heuristic**:

```
h(n) = min_hops(n, goal) × min_edge_weight
```

- `min_hops(n, goal)` = shortest number of edges from n to goal (found via BFS on unweighted graph)
- `min_edge_weight` = smallest edge cost in the entire graph

**Why this works (admissibility proof):**
- Any path from n to goal needs at least `min_hops` edges
- Each edge costs at least `min_edge_weight`
- So true cost >= min_hops × min_edge_weight = h(n)
- h(n) never overestimates → **admissible** ✓

**Consistency:**
- For any edge (n, n') with cost c: h(n) − h(n') ≤ min_edge_weight ≤ c
- Triangle inequality holds → **consistent** ✓

With an admissible & consistent heuristic, IDA* is guaranteed to return the optimal path.

## 3. Cost Function

IDA* uses:
```
f(n) = g(n) + h(n)
```

Where:
- **g(n)** = actual cost from source to n (sum of edges we've taken so far)
- **h(n)** = heuristic estimate of remaining cost to reach goal

The algorithm starts with threshold = h(source). Each iteration does a DFS but cuts off any path where f(n) exceeds the threshold. If we don't find the goal, the threshold gets bumped up to the smallest f-value that went over, and we try again. This way we gradually explore costlier paths until we hit the optimal one.

## 4. Why IDA*?

Reasons for choosing IDA* over other algorithms:

1. **Guaranteed optimal** — same as A* when heuristic is admissible
2. **Low memory** — only stores the current path (O(depth)), whereas A* keeps the whole open list in memory which can blow up
3. **Uses heuristic** — unlike BFS/Dijkstra which are blind, IDA* prunes bad paths early using h(n)
4. **Good fit for this problem** — the robot has limited battery so we want optimal routes without wasting computational resources

The downside is it re-visits some nodes across iterations, but for graphs of this size it's not a problem. The memory savings are worth it.

---

## 5. Implementation
"""

from collections import deque
import math
import sys


class PathStack:
    """
    Stack data structure used to maintain the current DFS path in IDA*.
    Has a fixed capacity (= number of nodes in the graph) since the path
    can never be longer than visiting every node once.
    """

    def __init__(self, capacity):
        self._stack = []
        self._capacity = capacity
        self._items_set = set()  # for O(1) membership checks (cycle detection)

    def push(self, item):
        """Add a node to the path. Prints error if stack is full."""
        if len(self._stack) >= self._capacity:
            print(f"Stack overflow: Cannot push '{item}' - path stack is full (capacity={self._capacity})")
            return False
        self._stack.append(item)
        self._items_set.add(item)
        return True

    def pop(self):
        """Remove and return the top node. Prints error if stack is empty."""
        if len(self._stack) == 0:
            print("Stack underflow: Cannot pop - path stack is empty!")
            return None
        item = self._stack.pop()
        self._items_set.discard(item)
        return item

    def peek(self):
        """Return top element without removing it."""
        if len(self._stack) == 0:
            print("Stack empty: Nothing to peek!")
            return None
        return self._stack[-1]

    def __contains__(self, item):
        """O(1) cycle detection."""
        return item in self._items_set

    def __len__(self):
        return len(self._stack)

    def to_list(self):
        """Return a copy of the stack as a list (bottom to top)."""
        return list(self._stack)

    def is_empty(self):
        return len(self._stack) == 0

    def is_full(self):
        return len(self._stack) >= self._capacity

"""### 5.1 Reading the Input File"""

def read_input(filename):
    """Parse input file and return list of test cases."""

    # try opening the file
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' does not exist!")
        return None
    except IOError as e:
        print(f"Error: Could not read file - {e}")
        return None

    # remove blank lines
    lines = [l.strip() for l in content.splitlines() if l.strip()]

    if len(lines) == 0:
        print("Error: Input file is empty!")
        return None

    cases = []
    i = 0

    while i < len(lines):
        # skip until we hit 'Road Connections'
        while i < len(lines) and 'road connections' not in lines[i].lower():
            i += 1
        if i >= len(lines):
            break
        i += 1  # move past that header line

        # now read the edges
        edges = []
        while i < len(lines) and not lines[i].lower().startswith('source'):
            line = lines[i]
            parts = line.split()

            if len(parts) == 3:
                # normal format like: MG_Road Electronic_City 2
                u, v = parts[0], parts[1]
                try:
                    w = int(parts[2])
                except ValueError:
                    print(f"Error: Weight '{parts[2]}' is not a valid integer in line: {line}")
                    return None

            elif len(parts) == 1:
                # compact format like: AB3
                token = parts[0]
                if len(token) < 3 or not token[0].isalpha() or not token[1].isalpha():
                    print(f"Error: Can't parse compact edge '{token}' - expected format like AB3")
                    return None
                u = token[0]
                v = token[1]
                try:
                    w = int(token[2:])
                except ValueError:
                    print(f"Error: Weight part '{token[2:]}' is not valid in edge '{token}'")
                    return None
            else:
                print(f"Error: Don't know how to parse this edge line: '{line}'")
                return None

            # weight must be positive
            if w <= 0:
                print(f"Error: Edge weight must be positive, got {w} for {u}-{v}")
                return None

            edges.append((u, v, w))
            i += 1

        # grab the source
        if i >= len(lines) or 'source' not in lines[i].lower():
            print("Error: Expected 'Source:' line but didn't find it")
            return None
        source = lines[i].split(':', 1)[1].strip()
        if not source:
            print("Error: Source is blank!")
            return None
        i += 1

        # grab the destination
        if i >= len(lines) or 'destination' not in lines[i].lower():
            print("Error: Expected 'Destination:' line but didn't find it")
            return None
        destination = lines[i].split(':', 1)[1].strip()
        if not destination:
            print("Error: Destination is blank!")
            return None
        i += 1

        if len(edges) == 0:
            print("Error: No edges found for this case")
            return None

        cases.append({
            'edges': edges,
            'source': source,
            'destination': destination
        })

    if len(cases) == 0:
        print("Error: Couldn't find any valid test cases in the file")
        return None

    return cases

"""### 5.2 Building the Graph
Using an adjacency list (dictionary of lists). Since roads are bidirectional, we add each edge both ways.
"""

def build_graph(edges):
    """Create adjacency list from edge list. Undirected graph."""
    graph = {}

    for u, v, w in edges:
        if u not in graph:
            graph[u] = []
        if v not in graph:
            graph[v] = []

        # add both directions since roads are two-way
        graph[u].append((v, w))
        graph[v].append((u, w))

    if len(graph) == 0:
        print("Warning: Graph is empty, nothing was added")

    return graph


def print_graph(graph):
    """Display the graph nicely."""
    print("\nGraph (Adjacency List):")
    if len(graph) == 0:
        print("  <empty graph>")
        return
    for node in sorted(graph.keys()):
        connections = [f"{nbr}({w})" for nbr, w in graph[node]]
        print(f"  {node} --> {connections}")

"""### 5.3 Computing the Heuristic
We do a BFS from the goal backwards to find how many hops each node is away, then multiply by the cheapest edge in the graph.
"""

def compute_heuristic(graph, goal):
    """Admissible heuristic: h(n) = min_hops_to_goal * min_edge_weight."""

    # first find the cheapest edge in the whole graph
    min_weight = math.inf
    for node in graph:
        for nbr, w in graph[node]:
            if w < min_weight:
                min_weight = w

    if min_weight == math.inf:
        # no edges at all
        print("Error: Graph has no edges!")
        return {}

    # BFS from goal to find hop distance to every reachable node
    hops = {goal: 0}
    queue = deque([goal])

    while queue:
        curr = queue.popleft()
        for neighbor, _ in graph[curr]:
            if neighbor not in hops:
                hops[neighbor] = hops[curr] + 1
                queue.append(neighbor)

    # now compute h(n) for each node
    h = {}
    for node in graph:
        if node in hops:
            h[node] = hops[node] * min_weight
        else:
            h[node] = math.inf  # can't reach goal from here

    return h

"""### 5.4 IDA* Algorithm
The main search. Does iterative deepening with f-cost as the bound.
"""

def ida_star(graph, source, destination):
    """
    IDA* search.
    Returns (path, cost, nodes_explored, visited_order)
    or (None, -1, 0, []) if no path.
    """

    # check source exists
    if source not in graph:
        print(f"Error: Source '{source}' doesn't exist in the graph!")
        return None, -1, 0, []

    # check destination exists
    if destination not in graph:
        print(f"Error: Destination '{destination}' doesn't exist in the graph!")
        return None, -1, 0, []

    # trivial case
    if source == destination:
        return [source], 0, 1, [source]

    # get heuristic values
    h = compute_heuristic(graph, destination)
    print(f"\n Heuristic values: {h}")

    if h.get(source, math.inf) == math.inf:
        print(f"Error: '{source}' cannot reach '{destination}' - no connecting path!")
        return None, -1, 0, []

    # PathStack capacity = number of nodes (longest possible acyclic path)
    path = PathStack(capacity=len(graph))
    path.push(source)
    print(f" Initial threshold = h({source}) = {h[source]}")

    nodes_explored = [0]
    visited_per_iteration = []   # list of lists, one per iteration
    current_iter_visited = []    # nodes visited in the current iteration
    answer = [None]
    iteration = [0]

    def dfs(g, threshold):
        """Recursive DFS with threshold cutoff."""
        node = path.peek()
        f = g + h[node]

        # if f exceeds threshold, cut this branch
        if f > threshold:
            print(f"   Pruned {node}: f({node}) = g({g}) + h({h[node]}) = {f} > threshold({threshold})")
            return f

        nodes_explored[0] += 1
        current_iter_visited.append(node)
        print(f"   Exploring {node}: g={g}, h={h[node]}, f={f} <= threshold({threshold})")
        print(f"   Current path: {' -> '.join(path.to_list())}")

        # did we reach the goal?
        if node == destination:
            answer[0] = (path.to_list(), g)
            print(f"   *** GOAL REACHED at {node} with cost {g} ***")
            print(f"   Final path: {' -> '.join(path.to_list())}")
            return -1  # signal that we found it

        next_threshold = math.inf

        for neighbor, cost in graph[node]:
            # skip nodes already in current path (avoid cycles)
            if neighbor in path:
                print(f"   Skipping {neighbor} (already in path - cycle avoided)")
                continue

            path.push(neighbor)  # go deeper
            t = dfs(g + cost, threshold)

            if t == -1:
                return -1  # found! bubble up
            if t < next_threshold:
                next_threshold = t

            path.pop()  # backtrack

        return next_threshold

    # start with threshold = h(source)
    threshold = h[source]

    while True:
        iteration[0] += 1
        current_iter_visited.clear()
        print(f" --- Iteration {iteration[0]}, threshold = {threshold} ---")
        t = dfs(0, threshold)

        visited_per_iteration.append(list(current_iter_visited))

        if t == -1:
            # found the optimal path!
            print(f" Goal found in iteration {iteration[0]}!")
            return answer[0][0], answer[0][1], nodes_explored[0], visited_per_iteration

        if t == math.inf:
            # exhausted all possibilities, no path
            print("Search exhausted - no path to destination.")
            return None, -1, nodes_explored[0], visited_per_iteration

        # bump up threshold and try again
        print(f" Threshold raised: {threshold} -> {t}")
        # reset path to just the source for the next iteration
        while not path.is_empty():
            path.pop()
        path.push(source)
        threshold = t

"""### 5.5 Putting it all together"""

def solve(cases, output_file='outputPSXX.txt'):
    """Run IDA* on all test cases and print + save results."""
    output_lines = []

    for idx, case in enumerate(cases, 1):
        print(f"\n{'='*55}")
        print(f"  CASE {idx}")
        print(f"{'='*55}")

        graph = build_graph(case['edges'])
        print_graph(graph)

        src = case['source']
        dst = case['destination']
        print(f"\nSource: {src}")
        print(f"Destination: {dst}")

        # run the search
        path, cost, explored, visited = ida_star(graph, src, dst)

        print(f"\n--- Results ---")
        if path is not None:
            path_str = ' -> '.join(path)

            # format visited sequence: show per iteration separated by |
            iter_strs = [' -> '.join(nodes) for nodes in visited]
            visited_str = ' | '.join(iter_strs)

            print(f"Optimal Path: {path_str}")
            print(f"Total Travel Cost: {cost}")
            print(f"Nodes Explored: {explored}")
            print(f"\nVisited Sequence (per iteration, separated by |):")
            for i, nodes in enumerate(visited, 1):
                print(f"  Iteration {i}: {' -> '.join(nodes)}")

            output_lines.append(f"Case {idx}:")
            output_lines.append(f"Source: {src}")
            output_lines.append(f"Destination: {dst}")
            output_lines.append(f"Optimal Path: {path_str}")
            output_lines.append(f"Total Travel Cost: {cost}")
            output_lines.append(f"Nodes Explored: {explored}")
            output_lines.append(f"Visited Sequence: {visited_str}")
            output_lines.append('')
        else:
            print("No path found.")
            output_lines.append(f"Case {idx}: No path found")
            output_lines.append('')

    # save to file
    try:
        with open(output_file, 'w') as f:
            f.write('\n'.join(output_lines))
        print(f"\n\nResults saved to '{output_file}'")
    except IOError as e:
        print(f"Error: Could not write to output file - {e}")

"""### 5.6 Running on the Input File"""

# read from input file
INPUT_FILE = 'inputPSXX.txt'
OUTPUT_FILE = 'outputPSXX.txt'

cases = read_input(INPUT_FILE)

if cases is not None:
    print(f"Successfully loaded {len(cases)} case(s) from '{INPUT_FILE}'")
    solve(cases, OUTPUT_FILE)
else:
    print("Failed to load input. Please check the file and try again.")

# ---

# ## 6. Error Handling Demonstrations

# Below we test that our code handles edge cases gracefully.

print("--- Test: Invalid source node ---")
test_edges = [('X', 'Y', 5), ('Y', 'Z', 3)]
test_graph = build_graph(test_edges)
result = ida_star(test_graph, 'A', 'Z')  # 'A' is not in graph
print(f"Result: {result}")
print()

print("--- Test: Invalid destination node ---")
test_edges = [('X', 'Y', 5), ('Y', 'Z', 3)]
test_graph = build_graph(test_edges)
result = ida_star(test_graph, 'X', 'W')  # 'W' not in graph
print(f"Result: {result}")
print()

print("--- Test: Source == Destination ---")
test_edges = [('A', 'B', 2), ('B', 'C', 3)]
test_graph = build_graph(test_edges)
path, cost, explored, visited = ida_star(test_graph, 'A', 'A')
print(f"Path: {path}, Cost: {cost}, Explored: {explored}")
print()

print("--- Test: No path between source and destination ---")
# Two separate components: {A,B} and {C,D}
test_edges = [('A', 'B', 1), ('C', 'D', 2)]
test_graph = build_graph(test_edges)
result = ida_star(test_graph, 'A', 'D')
print(f"Result: {result}")
print()

print("--- Test: Empty graph ---")
empty_graph = build_graph([])
result = ida_star(empty_graph, 'A', 'B')
print(f"Result: {result}")
print()

print("--- Test: Non-existent input file ---")
result = read_input('this_file_does_not_exist.txt')
print(f"Result: {result}")
print()

print("--- Test: Graph with only 2 nodes ---")
test_edges = [('Start', 'End', 10)]
test_graph = build_graph(test_edges)
path, cost, explored, visited = ida_star(test_graph, 'Start', 'End')
print(f"Path: {path}")
print(f"Cost: {cost}")
print(f"Explored: {explored}")
print()
