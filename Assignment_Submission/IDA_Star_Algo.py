# ─────────────────────────────────────────────────────────────────────────────
# Smart Waste Collection Robot Agent
# Bengaluru Smart City Initiative | Algorithm: Iterative Deepening A* (IDA*)

# Smart Waste Collection Robot Agent
# 
# 1. Problem Formulation
# The objective is to design a rational agent that efficiently transports waste between collection centers and processing plants while operating under strict battery and fuel constraints.

# * State Space (S): The complete set of waste collection centers and processing units represented as vertices in a weighted graph.
# * Initial State (S_0): The starting waste collection location (User-specified Source).
# * Goal State (G): The target waste processing unit (User-specified Destination).
# * Actions (A): Traversing from the current node to an adjacent node via a valid connecting road.
# * Path Cost (g(n)): The cumulative sum of edge weights (representing travel cost, distance, or fuel consumption) along the chosen route.
# * Solution: An ordered sequence of locations forming the optimal, least-cost path from S_0 to G.

# ## 2. PEAS Analysis
# To formalize the agent's operating context, we define its PEAS characteristics:
# * Performance Measure: Successfully reach the destination, strictly minimize total travel cost (fuel/distance), and optimize navigation efficiency by avoiding unnecessary node explorations.
# * Environment: Fully observable (the agent has access to the complete map), static, discrete, and deterministic road network.
# * Actuators: Mobility systems to traverse connecting edges (roads) between vertices.
# * Sensors: Localized graph-reading capabilities to identify the current location, valid adjacent pathways, and associated edge costs.

# ## 3. Algorithm Choice & Heuristic Design

# ### Algorithm Choice: IDA*
# Iterative Deepening A* (IDA*) combines A*'s optimal pathfinding with Depth-First Search's minimal memory footprint. 
# * Efficiency: Guided by an increasing cost threshold rather than storing all nodes, it is ideal for a robot with limited computational and battery resources.
# * Optimality: With an admissible heuristic, IDA* guarantees the optimal, least-cost route.

# ### Cost Function
# Nodes are evaluated using: f(n) = g(n) + h(n)
# * g(n): Actual cumulative travel cost from the source to node n.
# * h(n): Estimated remaining cost from node n to the destination.

# ### The Custom Heuristic
# We use a *relaxed problem* heuristic, assuming all edges cost the graph's absolute minimum weight.
# * d_{min} = minimum edge weight in the entire graph.
# * hops(n, goal) = minimum number of unweighted edges from n to the goal.

# Heuristic Function:
# h(n) = hops(n, goal) \times d_{min}

# ### Heuristic Properties
# * Admissibility (h(n) \le h*(n)): To reach the goal, the robot *must* traverse at least hops edges, each costing at least d_{min}. Therefore, h(n) represents the absolute minimum possible cost and never overestimates the true cost.
# * Consistency (h(n) \le c(n,m) + h(m)): The actual step cost between adjacent nodes c(n,m) is always \ge d_{min}$. This perfectly offsets the maximum possible 1-hop decrease in the remaining estimated cost.


# ─────────────────────────────────────────────────────────────────────────────

from collections import defaultdict, deque
import os
import sys


# ─────────────────────────────────────────────────────────────────────────────
# Bounded Stack
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# Bounded Data Structures + Graph + BFS-based Heuristic
# ─────────────────────────────────────────────────────────────────────────────
# Heuristic  h(n) = BFS_hops(n, goal) × min_edge_cost
#   • BFS runs on the unweighted undirected graph from the goal node.
#   • min_edge_cost is the smallest edge weight in the entire graph.
#   • Because every hop costs ≥ min_edge_cost, h(n) ≤ actual remaining cost
#     → the heuristic is ADMISSIBLE and CONSISTENT, guaranteeing optimality.
# ─────────────────────────────────────────────────────────────────────────────
class BoundedStack:
    """
    A LIFO stack with a fixed maximum capacity.

    Used by IDA* to maintain the current DFS path; capacity is set to the
    number of nodes in the graph (a simple path can visit each node at most once).

    Raises
    ------
    OverflowError : push() when the stack has reached its capacity.
    IndexError    : pop() or peek() when the stack is empty.
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError(
                f"[BoundedStack] Capacity must be a positive integer. Got {capacity}."
            )
        self._data     = []
        self._capacity = capacity

    # ── Mutating operations ───────────────────────────────────────────────────
    def push(self, item) -> None:
        """Push *item* onto the top of the stack."""
        if len(self._data) >= self._capacity:
            raise OverflowError(
                f"[BoundedStack] Stack is full (capacity={self._capacity}). "
                f"Cannot push '{item}'."
            )
        self._data.append(item)

    def pop(self):
        """Remove and return the top item."""
        if not self._data:
            raise IndexError(
                "[BoundedStack] Stack is empty. Cannot pop."
            )
        return self._data.pop()

    # ── Non-mutating helpers ──────────────────────────────────────────────────
    def peek(self):
        """Return the top item without removing it."""
        if not self._data:
            raise IndexError(
                "[BoundedStack] Stack is empty. Cannot peek."
            )
        return self._data[-1]

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def is_full(self) -> bool:
        return len(self._data) >= self._capacity

    def to_list(self) -> list:
        """Return a shallow copy of the internal list (bottom → top)."""
        return list(self._data)

    def __len__(self):
        return len(self._data)

    def __contains__(self, item):
        return item in self._data

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        top = self._data[-1] if self._data else 'empty'
        return f"BoundedStack(capacity={self._capacity}, size={len(self._data)}, top={top})"


# ─────────────────────────────────────────────────────────────────────────────
# Bounded Queue
# ─────────────────────────────────────────────────────────────────────────────

class BoundedQueue:
    """
    A FIFO queue with a fixed maximum capacity.

    Used by the BFS heuristic in Graph.compute_heuristic(); capacity is set to
    the number of nodes in the graph (each node is enqueued at most once).

    Raises
    ------
    OverflowError : enqueue() when the queue has reached its capacity.
    IndexError    : dequeue() when the queue is empty.
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError(
                f"[BoundedQueue] Capacity must be a positive integer. Got {capacity}."
            )
        self._data     = deque()
        self._capacity = capacity

    # ── Mutating operations ───────────────────────────────────────────────────
    def enqueue(self, item) -> None:
        """Add *item* to the back of the queue."""
        if len(self._data) >= self._capacity:
            raise OverflowError(
                f"[BoundedQueue] Queue is full (capacity={self._capacity}). "
                f"Cannot enqueue '{item}'."
            )
        self._data.append(item)

    def dequeue(self):
        """Remove and return the front item."""
        if not self._data:
            raise IndexError(
                "[BoundedQueue] Queue is empty. Cannot dequeue."
            )
        return self._data.popleft()

    # ── Non-mutating helpers ──────────────────────────────────────────────────
    def is_empty(self) -> bool:
        return len(self._data) == 0

    def is_full(self) -> bool:
        return len(self._data) >= self._capacity

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"BoundedQueue(capacity={self._capacity}, size={len(self._data)})"


# ─────────────────────────────────────────────────────────────────────────────
# Graph
# ─────────────────────────────────────────────────────────────────────────────

class Graph:
    """
    Undirected weighted graph for the Smart Waste Collection network.

    Attributes
    ----------
    graph        : adjacency list  {node: [(neighbour, weight), ...]}
    min_edge_cost: minimum edge weight seen across all add_edge() calls
    nodes        : set of all node names present in the graph
    max_nodes    : maximum number of distinct nodes allowed (None = unlimited)
    """

    def __init__(self, max_nodes: int = None):
        self.graph         = defaultdict(list)
        self.min_edge_cost = float('inf')
        self.nodes         = set()
        if max_nodes is not None and max_nodes <= 0:
            raise ValueError(
                f"[Graph] max_nodes must be a positive integer. Got {max_nodes}."
            )
        self.max_nodes = max_nodes

    # ── Edge insertion ────────────────────────────────────────────────────────
    def add_edge(self, u: str, v: str, weight: float) -> None:
        """
        Add an undirected edge between nodes u and v with the given weight.

        Parameters
        ----------
        u, v   : node names (non-empty strings)
        weight : travel cost / fuel consumption (must be > 0)

        Raises
        ------
        ValueError    : if node names are empty or weight is non-positive.
        OverflowError : if adding the edge's new node(s) would exceed max_nodes.
        """
        if not u or not v:
            raise ValueError(
                f"[add_edge] Node names must be non-empty strings. "
                f"Received: u='{u}', v='{v}'"
            )
        if weight <= 0:
            raise ValueError(
                f"[add_edge] Edge weight must be positive. "
                f"Received weight={weight} for edge ({u} ↔ {v})"
            )

        # ── Capacity guard: count only genuinely new nodes ────────────────────
        if self.max_nodes is not None:
            new_nodes = {n for n in (u, v) if n not in self.nodes}
            if len(self.nodes) + len(new_nodes) > self.max_nodes:
                raise OverflowError(
                    f"[Graph] Node capacity is full (max_nodes={self.max_nodes}). "
                    f"Cannot add edge ({u} ↔ {v}) – it would introduce "
                    f"{len(new_nodes)} new node(s) beyond the limit."
                )

        self.graph[u].append((v, weight))
        self.graph[v].append((u, weight))
        self.nodes.add(u)
        self.nodes.add(v)
        self.min_edge_cost = min(self.min_edge_cost, weight)

    # ── Neighbour access ──────────────────────────────────────────────────────
    def get_neighbors(self, node: str) -> list:
        """
        Return neighbours of *node* sorted by edge weight (ascending).
        Lower-cost roads are explored first, which prunes the IDA* search
        tree earlier and reduces total nodes explored.
        """
        if node not in self.nodes:
            print(f"[get_neighbors] Warning: node '{node}' not found in graph.")
            return []
        return sorted(self.graph[node], key=lambda x: x[1])

    # ── BFS heuristic ─────────────────────────────────────────────────────────
    def compute_heuristic(self, goal: str) -> dict:
        """
        Compute h(n) for every node using BFS on the unweighted graph.

        h(n) = hop_count(n → goal) × min_edge_cost

        Uses a BoundedQueue (capacity = number of nodes) for BFS traversal.
        Each node is enqueued at most once, so the queue never overflows.

        Parameters
        ----------
        goal : destination node name

        Returns
        -------
        dict  {node: h_value}   (unreachable nodes → float('inf'))
        """
        if goal not in self.nodes:
            raise ValueError(
                f"[compute_heuristic] Goal node '{goal}' not found in graph."
            )
        if self.min_edge_cost == float('inf'):
            raise ValueError(
                "[compute_heuristic] Graph has no edges; cannot compute heuristic."
            )

        # BFS – count hops from goal to every other node.
        # Capacity = total nodes: each node is enqueued at most once.
        bfs_queue = BoundedQueue(capacity=len(self.nodes))
        hops      = {goal: 0}
        bfs_queue.enqueue(goal)

        while not bfs_queue.is_empty():
            current = bfs_queue.dequeue()
            for neighbour, _ in self.graph[current]:
                if neighbour not in hops:
                    hops[neighbour] = hops[current] + 1
                    bfs_queue.enqueue(neighbour)   # safe: each node enqueued once

        # Build heuristic dict; nodes not reached by BFS are unreachable
        h = {}
        for node in self.nodes:
            if node in hops:
                h[node] = hops[node] * self.min_edge_cost
            else:
                h[node] = float('inf')

        return h


# ─────────────────────────────────────────────────────────────────────────────
# Input File Parser
# ─────────────────────────────────────────────────────────────────────────────
# Reads inputPS1.txt which may contain multiple CASE blocks.
#
# Expected block format (keywords are case-insensitive):
#   CASE   <n>
#   NODES  <n>
#   EDGES  <n>
#   <node1> <node2> <weight>     ← repeated EDGES times
#   HEURISTIC <node> <value>     ← parsed then discarded (heuristic is computed)
#   SOURCE      <node>
#   DESTINATION <node>
#
# Blank lines between blocks are tolerated.
# ─────────────────────────────────────────────────────────────────────────────

def parse_input(filename: str) -> list:
    """
    Parse *filename* and return a list of case dictionaries.

    Each dictionary has the keys:
        case_num    (int)   – 1-based case index
        source      (str)   – source node name
        destination (str)   – destination node name
        graph       (Graph) – populated Graph object

    Raises
    ------
    FileNotFoundError : if *filename* does not exist.
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(
            f"[parse_input] Input file '{filename}' not found."
        )

    with open(filename, 'r', encoding='utf-8') as fh:
        raw_lines = fh.readlines()

    # Strip whitespace and skip blank lines; keep (original_index, text) for
    # helpful error messages.
    lines = [
        (i + 1, ln.strip())
        for i, ln in enumerate(raw_lines)
        if ln.strip()
    ]

    cases           = []
    i               = 0
    total_lines     = len(lines)

    while i < total_lines:
        lineno, text = lines[i]
        tokens       = text.split()

        # ── Expect CASE keyword to start a new block ─────────────────────────
        if tokens[0].upper() != 'CASE':
            i += 1
            continue

        case_num = int(tokens[1]) if len(tokens) > 1 else len(cases) + 1
        i       += 1

        graph       = Graph()
        source      = None
        destination = None
        edge_count  = 0          # declared number of edges
        edges_read  = 0          # edges actually parsed
        in_edges    = False      # True while reading edge triples

        while i < total_lines:
            lineno, text = lines[i]
            tokens       = text.split()

            # New CASE starts → finish this block without consuming the line
            if tokens[0].upper() == 'CASE':
                break

            keyword = tokens[0].upper()

            if keyword == 'NODES':
                # Number of nodes – informational only (nodes added via edges)
                i += 1

            elif keyword == 'EDGES':
                edge_count = int(tokens[1])
                in_edges   = True
                i         += 1

            elif keyword == 'SOURCE':
                in_edges = False
                if len(tokens) < 2:
                    print(f"[parse_input] Line {lineno}: SOURCE keyword missing node name – skipping.")
                else:
                    source = tokens[1]
                i += 1

            elif keyword == 'DESTINATION':
                in_edges = False
                if len(tokens) < 2:
                    print(f"[parse_input] Line {lineno}: DESTINATION keyword missing node name – skipping.")
                else:
                    destination = tokens[1]
                i += 1

            elif in_edges and len(tokens) == 3:
                # Edge definition: <node1> <node2> <weight>
                u, v = tokens[0], tokens[1]
                try:
                    weight = float(tokens[2])
                    graph.add_edge(u, v, weight)
                    edges_read += 1
                except ValueError as exc:
                    print(f"[parse_input] Line {lineno}: invalid edge – {exc}")
                i += 1

            else:
                # Unrecognised line inside a block – skip gracefully
                i += 1

        # ── Validate the completed block ──────────────────────────────────────
        if source is None:
            print(f"[parse_input] Case {case_num}: SOURCE not found – case skipped.")
            continue
        if destination is None:
            print(f"[parse_input] Case {case_num}: DESTINATION not found – case skipped.")
            continue
        if source not in graph.nodes:
            print(
                f"[parse_input] Case {case_num}: SOURCE '{source}' is not a node in the graph – case skipped."
            )
            continue
        if destination not in graph.nodes:
            print(
                f"[parse_input] Case {case_num}: DESTINATION '{destination}' is not a node in the graph – case skipped."
            )
            continue

        cases.append({
            'case_num'   : case_num,
            'source'     : source,
            'destination': destination,
            'graph'      : graph,
        })

    if not cases:
        print("[parse_input] Warning: no valid cases found in input file.")

    return cases


# ─────────────────────────────────────────────────────────────────────────────
# IDA* Algorithm
# ─────────────────────────────────────────────────────────────────────────────
# IDA* (Iterative Deepening A*) combines the memory efficiency of DFS with
# the informed search of A*.
#
# Algorithm overview
# ──────────────────
# 1. Set initial f-cost threshold  T = h(start)
# 2. Run a depth-first search (DFS) where a branch is pruned as soon as
#    f(n) = g(n) + h(n) exceeds T.
# 3. If the goal is found within T → return the path (optimal).
# 4. Otherwise, update T to the minimum f-value that exceeded T, and repeat.
#
# Cost function
# ─────────────
#   g(n) = cumulative edge-weight cost from start to n along the current path.
#   h(n) = BFS_hops(n, goal) × min_edge_cost   (admissible heuristic)
#   f(n) = g(n) + h(n)                          (estimated total cost)
#
# Properties
# ──────────
#   Complete  : Yes (finds a solution if one exists on a finite graph)
#   Optimal   : Yes (because h is admissible)
#   Space     : O(b × d)  – only the current path is stored (vs O(b^d) for A*)
#   Time      : O(b^d)    – same asymptotic bound as A* in the worst case
# ─────────────────────────────────────────────────────────────────────────────

def ida_star(graph: Graph, start: str, goal: str):
    """
    Run IDA* on *graph* from *start* to *goal*.

    The DFS path is maintained with a BoundedStack (capacity = number of nodes).
    Because cycle detection prevents revisiting, the stack never overflows.
    An IndexError from pop() would indicate a logic error in the search.

    Parameters
    ----------
    graph : Graph   – populated Graph instance
    start : str     – source node name
    goal  : str     – destination node name

    Returns
    -------
    path           : list[str] – optimal path (start … goal), or None
    cost           : float     – total travel cost,           or float('inf')
    nodes_explored : int       – total search() calls (all iterations)
    """
    # ── Input validation ──────────────────────────────────────────────────────
    if start not in graph.nodes:
        print(f"[ida_star] Error: source node '{start}' not found in graph.")
        return None, float('inf'), 0
    if goal not in graph.nodes:
        print(f"[ida_star] Error: goal node '{goal}' not found in graph.")
        return None, float('inf'), 0

    # ── Pre-compute heuristic for every node ──────────────────────────────────
    h = graph.compute_heuristic(goal)

    if h[start] == float('inf'):
        print(f"[ida_star] Goal '{goal}' is not reachable from '{start}'.")
        return None, float('inf'), 0

    # ── Shared mutable counter (modified inside the nested function) ──────────
    nodes_explored = [0]   # list used so the nested function can mutate it

    # ── Recursive depth-limited search ───────────────────────────────────────
    def search(path: BoundedStack, g: float, threshold: float):
        """
        Depth-first search pruned by f-cost threshold.

        Parameters
        ----------
        path      : BoundedStack holding the current DFS path (top = current node)
        g         : cost accumulated from start to path.peek()
        threshold : current f-cost limit

        Returns
        -------
        (result, found_path, found_cost)
          result == -1          → goal reached; found_path and found_cost valid
          result == float('inf')→ branch exhausted with no successor
          result == f_value     → minimum f exceeding threshold in this subtree
        """
        node = path.peek()              # BoundedStack: raises IndexError if empty
        nodes_explored[0] += 1         # count every node visit
        f    = g + h.get(node, float('inf'))

        # ── Prune branch ──────────────────────────────────────────────────────
        if f > threshold:
            return f, None, 0.0

        # ── Goal check ────────────────────────────────────────────────────────
        if node == goal:
            return -1, path.to_list(), g

        # ── Expand neighbours ─────────────────────────────────────────────────
        minimum = float('inf')
        for neighbour, edge_cost in graph.get_neighbors(node):
            if neighbour in path:
                continue                # avoid cycles on the current path

            path.push(neighbour)        # BoundedStack: raises OverflowError if full
            result, found_path, found_cost = search(path, g + edge_cost, threshold)
            path.pop()                  # BoundedStack: raises IndexError if empty

            if result == -1:            # goal found – propagate upward
                return -1, found_path, found_cost

            if result < minimum:
                minimum = result        # track tightest next threshold

        return minimum, None, 0.0

    # ── Outer IDA* loop ───────────────────────────────────────────────────────
    threshold = h[start]              # initial bound = heuristic of start node

    # BoundedStack capacity = node count; a simple path visits each node once
    path = BoundedStack(capacity=len(graph.nodes))
    path.push(start)

    while True:
        result, found_path, found_cost = search(path, 0.0, threshold)

        if result == -1:              # optimal path found
            return found_path, found_cost, nodes_explored[0]

        if result == float('inf'):    # goal is unreachable
            print(f"[ida_star] No path from '{start}' to '{goal}'.")
            return None, float('inf'), nodes_explored[0]

        threshold = result            # raise bound to next candidate f-value


# ─────────────────────────────────────────────────────────────────────────────
# Output Formatter + Main Execution
# ─────────────────────────────────────────────────────────────────────────────
# Reads  : input file provided by user
# Runs   : IDA* for each case
# Writes : outputPS1.txt  AND  prints the same to stdout
# ─────────────────────────────────────────────────────────────────────────────

INPUT_FILE  = 'inputPS1.txt'
OUTPUT_FILE = 'outputPS1.txt'

BORDER = "═══════════════════════════════════════"


def format_cost(cost: float) -> str:
    """Return cost as an integer string if it is a whole number, else float."""
    return str(int(cost)) if cost == int(cost) else str(cost)


def format_case_result(case_num: int, source: str, destination: str,
                        path, cost: float, nodes_explored: int) -> str:
    """
    Build the output block for one case.

    Output format
    ─────────────
    ═══════════════════════════════════════
      SMART WASTE COLLECTION ROUTE OPTIMIZER
    ═══════════════════════════════════════

    SOURCE: <node>
    DESTINATION: <node>

    OPTIMAL PATH FOUND:
    <node> → <node> → ...

    ROUTE DETAILS:
    ├─ Total Travel Cost: <cost> units
    ├─ Nodes Explored: <count> nodes
    └─ Path Length: <hops> hops

    SEQUENCE OF VISITED LOCATIONS:
    1. <node>
    2. <node>
    ...
    ═══════════════════════════════════════
    """
    output  = BORDER + "\n"
    output += "  SMART WASTE COLLECTION ROUTE OPTIMIZER\n"
    output += BORDER + "\n\n"
    output += f"SOURCE: {source}\n"
    output += f"DESTINATION: {destination}\n\n"

    if path is None:
        output += "OPTIMAL PATH FOUND:\n"
        output += "No path found\n\n"
        output += "ROUTE DETAILS:\n"
        output += "├─ Total Travel Cost: N/A\n"
        output += f"├─ Nodes Explored: {nodes_explored} nodes\n"
        output += "└─ Path Length: N/A\n\n"
        output += "SEQUENCE OF VISITED LOCATIONS:\n"
        output += "N/A\n"
    else:
        output += "OPTIMAL PATH FOUND:\n"
        output += " → ".join(path) + "\n\n"
        output += "ROUTE DETAILS:\n"
        output += f"├─ Total Travel Cost: {format_cost(cost)} units\n"
        output += f"├─ Nodes Explored: {nodes_explored} nodes\n"
        output += f"└─ Path Length: {len(path) - 1} hops\n\n"
        output += "SEQUENCE OF VISITED LOCATIONS:\n"
        for i, loc in enumerate(path, 1):
            output += f"{i}. {loc}\n"

    output += BORDER + "\n"
    return output


def write_output(blocks: list, output_file: str) -> None:
    """
    Write all formatted result blocks to *output_file* and print to stdout.

    Parameters
    ----------
    blocks      : list of formatted result strings (one per case)
    output_file : path to the output text file
    """
    full_output = "\n".join(blocks)

    with open(output_file, 'w', encoding='utf-8') as fh:
        fh.write(full_output + "\n")

    print(full_output)
    print(f"\n[Output written to '{output_file}']")


def get_input_filename() -> str:
    """Ask the user for the input file path, defaulting to INPUT_FILE."""
    user_input = input(f"Enter input file path [{INPUT_FILE}]: ").strip()
    return user_input if user_input else INPUT_FILE


# ── Main execution ────────────────────────────────────────────────────────────

def main(input_file: str = None, output_file: str = OUTPUT_FILE) -> None:
    """
    End-to-end driver: parse → search → format → write.

    PEAS description of the Smart Waste Collection Robot Agent
    ──────────────────────────────────────────────────────────
    Performance : Minimise total travel cost (edge-weight sum on optimal path)
    Environment : Weighted road network (static, fully observable, deterministic)
    Actuators   : Move the robot between directly connected waste collection nodes
    Sensors     : Current location, edge weights, pre-built heuristic table
    """
    if input_file is None:
        input_file = get_input_filename()

    print(f"Reading input from '{input_file}' …\n")

    # ── Parse input ───────────────────────────────────────────────────────────
    try:
        cases = parse_input(input_file)
    except FileNotFoundError as exc:
        print(exc)
        return

    if not cases:
        print("No valid cases to process.")
        return

    # ── Run IDA* for each case ────────────────────────────────────────────────
    result_blocks = []

    for case in cases:
        n   = case['case_num']
        src = case['source']
        dst = case['destination']
        g   = case['graph']

        print(f"--- Case {n}: {src} -> {dst} ---")

        path, cost, explored = ida_star(g, src, dst)
        block = format_case_result(n, src, dst, path, cost, explored)
        result_blocks.append(block)

    # ── Write consolidated output ─────────────────────────────────────────────
    print("\n" + "=" * 50)
    write_output(result_blocks, output_file)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(input_file=sys.argv[1])
    else:
        main()
