from collections import deque
import math
import sys

# ─────────────────────────────────────────────────────────────────────────────
# Cell 1 │ Bounded PathStack for DFS + Cycle Detection
# ─────────────────────────────────────────────────────────────────────────────
# PathStack maintains the current IDA* path with a fixed capacity equal to
# the number of nodes in the graph. It supports push/pop/peek, and uses an
# internal set for O(1) membership tests.
#   • Prevents stack overflow when path length would exceed graph size.
#   • Enables cycle avoidance in DFS by checking if a neighbor is already
#     in the current path.
#   • Provides path state for backtracking and visited-sequence reporting.
# ─────────────────────────────────────────────────────────────────────────────


class PathStack:
    """
    Stack data structure used to maintain the current DFS path in IDA*.
    Has a fixed capacity (= number of nodes in the graph) since the path
    can never be longer than visiting every node once.

    The stack methods print informative error messages when a push is
    attempted on a full stack or when pop/peek is attempted on an empty stack.
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


# ─────────────────────────────────────────────────────────────────────────────
# Cell 2 │ Input Parsing and Validation
# ─────────────────────────────────────────────────────────────────────────────
# read_input() reads a text file and converts it into structured test cases.
#   • Skips blank lines, looks for "Road Connections" blocks, then reads
#     edges until "Source" is encountered.
#   • Validates edge format, distinct endpoints, positive integer weights,
#     and non-empty source/destination values.
#   • Returns a list of cases where each case contains edges, source, and
#     destination.
# ─────────────────────────────────────────────────────────────────────────────


def read_input(filename):
    """Parse an input file into structured graph search test cases.

    Each test case includes a list of weighted edges, source node,
    and destination node. This function validates edge format,
    ensures positive weights and distinct endpoints, and skips
    blank lines and headers until valid cases are found.
    Args:
        filename: The path to the input text file to parse.
    Returns:
        A list of case dictionaries or None if parsing fails.
    """
    
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
            else:
                print(
                    f"Error: Don't know how to parse this edge line: '{line}' - expected format 'U V W'"
                )
                return None
            
            if u == v:
                print(f"Error: Edge endpoints must be distinct, got '{u}-{v}'")
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


# ─────────────────────────────────────────────────────────────────────────────
# Cell 3 │ Graph Construction and Display
# ─────────────────────────────────────────────────────────────────────────────
# build_graph() constructs an undirected adjacency list from the edge list.
#   • Adds each edge in both directions because roads are bidirectional.
#   • Ensures every node appears in the graph dictionary even if it has
#     only one neighbor.
# print_graph() prints the adjacency list neatly.
# ─────────────────────────────────────────────────────────────────────────────


def build_graph(edges):
    """Create an undirected adjacency list from a weighted edge list.

    Each edge is added in both directions to represent a bidirectional
    road network. The function also ensures every node appears in the
    returned graph even if it has only a single neighbor.
    Args:
        edges: A list of tuples (u, v, w) representing weighted edges.
    Returns:
        A dictionary mapping nodes to lists of (neighbor, weight) pairs.
    """
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
    """Display the graph adjacency list in a readable format.

    Prints each node and its connected neighbors along with edge costs.
    Handles empty graphs gracefully and helps verify parsed input
    before running the search algorithm.
    Args:
        graph: The adjacency list to print.
    Returns:
        None.
    """
    print("\nGraph (Adjacency List):")
    if len(graph) == 0:
        print("  <empty graph>")
        return
    for node in sorted(graph.keys()):
        connections = [f"{nbr}({w})" for nbr, w in graph[node]]
        print(f"  {node} --> {connections}")


# ─────────────────────────────────────────────────────────────────────────────
# Cell 4 │ Heuristic: BFS Hop Distance × Minimum Edge Cost
# ─────────────────────────────────────────────────────────────────────────────
# compute_heuristic() builds an admissible, consistent heuristic for IDA*.
#   • Finds the smallest edge weight in the entire graph: min_weight.
#   • Runs BFS from the goal node on the unweighted graph to compute the
#     minimum hop count from every node to the goal.
#   • Sets h(n) = hops(n, goal) × min_weight.
#   • If a node cannot reach the goal, h(n) = infinity.
# Because every actual move costs at least min_weight, this heuristic never
# overestimates and is consistent.
# ─────────────────────────────────────────────────────────────────────────────


def compute_heuristic(graph, goal):
    """Compute an admissible heuristic map for IDA* search.

    Uses BFS from the goal to determine minimum hop counts for
    every reachable node, then multiplies the hop distance by the
    smallest edge weight in the graph. This yields a heuristic that
    never overestimates and remains consistent for IDA*.
    Args:
        graph: The adjacency list representing the weighted graph.
        goal: The goal node for which heuristic values are computed.
    Returns:
        A dict mapping nodes to heuristic cost estimates.
    """
    
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


# ─────────────────────────────────────────────────────────────────────────────
# Cell 5 │ IDA* Search with Iterative Thresholding
# ─────────────────────────────────────────────────────────────────────────────
# ida_star() performs the main search and returns optimal path metrics.
#   • Validates source/destination existence and handles source == goal.
#   • Computes the heuristic and sets initial threshold = h(source).
#   • Uses recursive DFS with f(n)=g(n)+h(n); prunes branches where
#     f > threshold.
#   • Tracks:
#       - nodes_evaluated: every node considered before pruning
#       - nodes_expanded: nodes that pass the threshold and generate children
#       - visited_per_iteration: nodes explored in each threshold iteration
#   • Avoids cycles by checking the current path set before pushing neighbors.
#   • When the goal is reached, returns the optimal path and cost.
#   • If no path exists, returns None and signals exhaustion.
# ─────────────────────────────────────────────────────────────────────────────


def ida_star(graph, source, destination):
    """Perform IDA* search on the weighted graph from source to destination.

    Uses iterative deepening with f(n)=g(n)+h(n) to prune expensive paths.
    Detects cycles via the current path stack and expands nodes only when
    the f-cost stays within the threshold. Returns the optimal path, cost,
    expansion metrics, and visited node order, or None when no path exists.
    Args:
        graph: The adjacency list of the weighted graph.
        source: The starting node for the search.
        destination: The target goal node for the search.
    Returns:
        A tuple (path, cost, nodes_expanded, nodes_evaluated, visited_order)
        or (None, -1, 0, 0, []) if no path is found.
    """
    
    # check source exists
    if source not in graph:
        print(f"Error: Source '{source}' doesn't exist in the graph!")
        return None, -1, 0, 0, []
    
    # check destination exists
    if destination not in graph:
        print(f"Error: Destination '{destination}' doesn't exist in the graph!")
        return None, -1, 0, 0, []
    
    # trivial case
    if source == destination:
        return [source], 0, 1, 1, [[source]]
    
    # get heuristic values
    h = compute_heuristic(graph, destination)
    print(f"\n Heuristic values: {h}")
    
    if h.get(source, math.inf) == math.inf:
        print(f"Error: '{source}' cannot reach '{destination}' - no connecting path!")
        return None, -1, 0, 0, []
    
    # PathStack capacity = number of nodes (longest possible acyclic path)
    path = PathStack(capacity=len(graph))
    path.push(source)
    print(f" Initial threshold = h({source}) = {h[source]}")
    
    nodes_evaluated = [0]   # every node the algorithm looks at (including pruned)
    nodes_expanded = [0]    # nodes that pass threshold check and iterate neighbors
    visited_per_iteration = []   # list of lists, one per iteration
    current_iter_visited = []    # nodes that passed threshold in the current iteration
    answer = [None]
    iteration = [0]
    
    def dfs(g, threshold):
        """Recursive DFS helper for the current IDA* threshold iteration.

        Evaluates the current node, prunes branches whose f-cost exceeds the
        threshold, records visited nodes, and returns the next threshold
        estimate or -1 when the goal is found.
        Args:
            g: The cumulative cost from source to current node.
            threshold: The current f-cost threshold for pruning.
        Returns:
            The next threshold estimate or -1 if the goal is reached.
        """
        node = path.peek()
        f = g + h[node]
        
        # count every node the algorithm evaluates (before threshold check)
        nodes_evaluated[0] += 1
        
        # if f exceeds threshold, cut this branch
        if f > threshold:
            print(f"   Pruned {node}: f({node}) = g({g}) + h({h[node]}) = {f} > threshold({threshold})")
            return f
        
        # node passed the threshold — record it in the visited sequence
        current_iter_visited.append(node)
        
        print(f"   Exploring {node}: g={g}, h={h[node]}, f={f} <= threshold({threshold})")
        print(f"   Current path: {' -> '.join(path.to_list())}")
        
        # did we reach the goal?
        if node == destination:
            answer[0] = (path.to_list(), g)
            print(f"   *** GOAL REACHED at {node} with cost {g} ***")
            print(f"   Final path: {' -> '.join(path.to_list())}")
            return -1  # signal that we found it
        
        # node is not the goal and passes threshold — it gets expanded
        nodes_expanded[0] += 1
        
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
            return answer[0][0], answer[0][1], nodes_expanded[0], nodes_evaluated[0], visited_per_iteration
        
        if t == math.inf:
            # exhausted all possibilities, no path
            print("Search exhausted - no path to destination.")
            return None, -1, nodes_expanded[0], nodes_evaluated[0], visited_per_iteration
        
        # bump up threshold and try again
        print(f" Threshold raised: {threshold} -> {t}")
        # reset path to just the source for the next iteration
        while not path.is_empty():
            path.pop()
        path.push(source)
        threshold = t


# ─────────────────────────────────────────────────────────────────────────────
# Cell 6 │ Execution and Output Writing
# ─────────────────────────────────────────────────────────────────────────────
# solve() runs IDA* for each parsed test case and records results.
#   • Builds the graph, prints the graph, source, and destination.
#   • Runs ida_star() and prints the optimal path, cost, nodes expanded,
#     visited sequence per iteration, and nodes evaluated.
#   • Writes case summaries to an output file.
# ─────────────────────────────────────────────────────────────────────────────


def solve(cases, output_file='outputPS01.txt'):
    """Run IDA* for each parsed test case and save the summarized output.

    Builds the graph for each case, invokes ida_star, and prints the
    optimal path, total cost, visited sequence, and node metrics.
    Also writes the results to the specified output file.
    Args:
        cases: A list of parsed test cases from read_input().
        output_file: The path where summary results are written.
    Returns:
        None.
    """
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
        path, cost, expanded, evaluated, visited = ida_star(graph, src, dst)
        
        print(f"\n--- Results ---")
        if path is not None:
            path_str = ' -> '.join(path)
            
            # format visited sequence: show per iteration separated by |
            iter_strs = [' -> '.join(nodes) for nodes in visited]
            visited_str = ' | '.join(iter_strs)
            
            print(f"Optimal Path: {path_str}")
            print(f"Total Travel Cost: {cost} units")
            print(f"Nodes Explored: {expanded} nodes")
            print(f"\nVisited Sequence (per iteration, separated by |):")
            for i, nodes in enumerate(visited, 1):
                print(f"  Iteration {i}: {' -> '.join(nodes)}")
            print(f"\nNodes Evaluated: {evaluated} nodes")
            
            output_lines.append(f"Case {idx}:")
            output_lines.append(f"Source: {src}")
            output_lines.append(f"Destination: {dst}")
            output_lines.append(f"Optimal Path: {path_str}")
            output_lines.append(f"Total Travel Cost: {cost} units")
            output_lines.append(f"Nodes Explored: {expanded} nodes")
            output_lines.append(f"Visited Sequence (Pipe Separtion): {visited_str}")
            output_lines.append(f"Nodes Evaluated: {evaluated} nodes")
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


def main(input_file='inputPS01.txt', output_file='outputPS01.txt'):
    """Load input cases from a file, run the solver, and save results.

    Uses default filenames when no command-line argument is provided.
    Prints whether input was loaded successfully and then launches solve().
    Args:
        input_file: The path to the input file to parse.
        output_file: The path to the output file where results are written.
    Returns:
        None.
    """
    cases = read_input(input_file)
    if cases is not None:
        print(f"Successfully loaded {len(cases)} case(s) from '{input_file}'")
        solve(cases, output_file)
    else:
        print("Failed to load input. Please check the file and try again.")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(input_file=sys.argv[1])
    else:
        main()
