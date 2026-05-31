# 🤖 Smart Waste Collection Agent - Assignment 1 (PS1)

> **Intelligent Path-Finding System for Urban Waste Management using IDA* Algorithm**

---

## 📌 Quick Reference

| Aspect | Details |
|--------|---------|
| **Course** | Artificial Intelligence & Computational Intelligence |
| **Weightage** | 12% |
| **Deadline** | June 8, 2026, 11:55 PM IST |
| **Primary Focus** | IDA* Algorithm Implementation & Route Optimization |
| **Submission** | Single ZIP file via Taxila |

---

## 🎯 Executive Summary

This assignment challenges you to build an **intelligent waste collection robot system** that:
- ✅ Operates within Bengaluru's complex waste management network
- ✅ Finds **cost-optimal routes** between collection points
- ✅ Implements the **IDA* (Iterative Deepening A*) algorithm**
- ✅ Handles real-world constraints (battery, fuel efficiency, weighted networks)
- ✅ Provides transparent path exploration and cost analysis

**Core Objective:** Implement a generalized, production-ready path-finding engine that combines memory efficiency with solution optimality.

---

## 🏗️ Problem Architecture

### PEAS Analysis Framework

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT DEFINITION                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PERFORMANCE MEASURE                                        │
│  • Minimize total travel cost (distance/fuel/time)         │
│  • Reduce nodes explored (memory efficiency)               │
│  • Guarantee optimal solution                              │
│                                                              │
│  ENVIRONMENT                                                │
│  • Weighted undirected graph (city road network)           │
│  • Static topology (roads don't change during journey)     │
│  • Fully observable (all costs known in advance)           │
│  • Deterministic (same route = same cost)                  │
│                                                              │
│  ACTUATORS                                                  │
│  • Movement along connected roads/edges                    │
│  • Route execution between adjacent nodes                  │
│                                                              │
│  SENSORS                                                    │
│  • Current location awareness                              │
│  • Complete road network information                       │
│  • Real-time cost tracking                                 │
│  • Destination coordinates                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Problem Context

The **Municipal Smart City Initiative** demands:
1. **Efficiency Constraints:** Limited battery power, fuel consumption optimization
2. **Network Complexity:** Multiple waste processing zones with weighted connections
3. **User Flexibility:** Support arbitrary source/destination pairs
4. **Cost Optimization:** Guaranteed minimum-cost path solutions

---

## 🔍 Key Requirements Analysis

### 1️⃣ Algorithm Selection: IDA* (Iterative Deepening A*)

**Why IDA* is Mandatory:**

```
┌─────────────────────────────────────────────────┐
│        Algorithm Comparison Matrix              │
├──────────────┬─────────┬────────┬──────────────┤
│ Algorithm    │ Optimal │ Memory │ Time         │
├──────────────┼─────────┼────────┼──────────────┤
│ Dijkstra     │ ✓       │ O(n²)  │ O(n log n)   │
│ A*           │ ✓       │ O(n²)  │ Better avg   │
│ IDA*         │ ✓       │ O(h)   │ O(n log n)   │ ✨ BEST
│ DFS          │ ✗       │ O(h)   │ O(n)         │
│ BFS          │ ✓       │ O(n)   │ Slower       │
└──────────────┴─────────┴────────┴──────────────┘

Key Advantage: IDA* = A* Optimality + DFS Memory Efficiency
```

**Core Benefits:**
- **Memory Efficient:** Uses O(h) space instead of O(n) like standard A*
- **Guarantees Optimality:** Finds guaranteed minimum-cost path
- **Avoids Overestimation:** Iterative deepening prevents heuristic bias
- **Space-Conscious:** Perfect for resource-constrained robots

### 2️⃣ Heuristic Strategy

**Admissible Heuristic Function:**

```python
# Heuristic Type: Euclidean Distance
h(n) = √[(x_destination - x_n)² + (y_destination - y_n)²]

# Or: Manhattan Distance (for grid-based networks)
h(n) = |x_destination - x_n| + |y_destination - y_n|
```

**Properties:**
- **Admissible:** Never overestimates actual cost (h(n) ≤ actual_cost(n→goal))
- **Consistent:** h(n) ≤ cost(n→n') + h(n') for all neighbors n'
- **Informed Search:** Significantly reduces search space compared to uninformed methods

**Justification:**
- Based on geographical coordinates of waste collection centers
- Straight-line distance = lower bound on actual road distance
- Zero heuristic (h=0) degrades to Dijkstra; tuned heuristic accelerates search

### 3️⃣ Cost Functions

```
f(n) = g(n) + h(n)  [Total estimated cost from START through n to GOAL]

where:
  g(n) = Actual cost from SOURCE to current node n
         (Sum of edge weights traversed)
  
  h(n) = Estimated cost from node n to DESTINATION
         (Heuristic approximation - Euclidean/Manhattan)
```

**Cost Model:**
- **Road Weights:** Represent distance, fuel consumption, or time
- **Cumulative Path Cost:** g(n) only increases as we go deeper
- **Heuristic Estimate:** h(n) predicts remaining distance

---

## 📋 Detailed Requirements Specification

### A. Deliverables Checklist

#### ✅ **designPS01_[GroupId].pdf** (Technical Design Document)
**Maximum 4 Pages | Required Sections:**

- [ ] **PEAS Analysis** - Complete agent environment breakdown
- [ ] **Heuristic Strategy** - Distance metric & admissibility proof
- [ ] **IDA* Explanation** - Algorithm pseudocode & trace example
- [ ] **Alternate Approach** - Different algorithm with comparative analysis
- [ ] **Performance Metrics** - Expected complexity for test cases

#### ✅ **[GroupId]_Contribution.xlsx** (Group Accountability)
**Columns Required:**
- Student Registration Number
- Name
- Percentage Contribution (%) - Must sum to 100%

#### ✅ **inputPS01.txt** (Test Case Input)
**Strict Format:**
```
[Number of Locations]
[Number of Roads]
[Location1] [Location2] [Cost]
...
[Source]
[Destination]
```

#### ✅ **outputPS01.txt** (Algorithm Output)
**Exact Format Required:**
```
OPTIMAL_PATH: [Start] → [Node2] → [Node3] → ... → [End]
TOTAL_COST: [X]
NODES_EXPLORED: [N]
VISITED_SEQUENCE: [[Location1, Location2, ..., LocationN]]
```

#### ✅ **solution.py** (Complete Implementation)
- **Single File Requirement:** No fragmented code across multiple files
- **Python Notebook/Script:** Can be `.py` or `.ipynb`
- **No Hardcoding:** Generic for any input format
- **Modular Functions:**
  - `build_graph()`
  - `heuristic(node, goal)`
  - `ida_star(graph, start, goal)`
  - `main(input_file, output_file)`

#### ✅ **[GroupId]_A1_PS01_[YYYYMMDD].zip** (Submission Package)
**All above files compressed together**
- Example: `G026_A1_PS01_20260531.zip`

---

### B. Test Cases & Expected Behavior

#### 🧪 Test Case 1: Bengaluru Waste Network

```
Graph Structure:
┌─────────────────────────────────────────┐
│        MG_Road (START)                  │
│         /  \                            │
│        2    4                           │
│       /      \                          │
│  Electronic  Koramangala               │
│  _City    \    \                       │
│    |       \    3                      │
│    2      Hebbal                       │
│    |       /                           │
│ White--6--Jayan     ↓ 5               │
│ field     agar----Yelahanka (END)     │
│    |       \       ↑                   │
│    4        2     /                    │
│     \      /-----/                     │
│      └────┘                            │
└─────────────────────────────────────────┘

Locations: MG_Road, Electronic_City, Whitefield, Koramangala, Hebbal, Yelahanka
Edges:
  MG_Road ↔ Electronic_City (cost: 2)
  MG_Road ↔ Koramangala (cost: 4)
  Electronic_City ↔ Whitefield (cost: 2)
  Whitefield ↔ Yelahanka (cost: 4)
  Whitefield ↔ Jayanagar (cost: 6)
  Jayanagar ↔ Yelahanka (cost: 2)
  Koramangala ↔ Hebbal (cost: 3)
  Hebbal ↔ Yelahanka (cost: 5)

Query: Path from MG_Road to Yelahanka
Expected Optimal: MG_Road → Electronic_City → Whitefield → Yelahanka
Expected Cost: 2 + 2 + 4 = 8
```

#### 🧪 Test Case 2: Generic Graph

```
Graph Structure:
        A (START)
       /|\
      3 2 
     /   \
    B     C (GOAL: E)
    |    /|\
    4   1 7
    |  /   \
    D←─────E

Edges:
  A ↔ B (cost: 3)
  A ↔ C (cost: 2)
  B ↔ D (cost: 4)
  C ↔ D (cost: 1)
  C ↔ E (cost: 7)
  D ↔ E (cost: 2)

Query: Path from A to E
Expected Optimal: A → C → D → E
Expected Cost: 2 + 1 + 2 = 5
Alternative: A → B → D → E = 3 + 4 + 2 = 9 (Suboptimal)
```

---

### C. Output Format Specification

**CRITICAL:** Output must match this exact format character-for-character:

```
═══════════════════════════════════════
  SMART WASTE COLLECTION ROUTE OPTIMIZER
═══════════════════════════════════════

SOURCE: [Location]
DESTINATION: [Location]

OPTIMAL PATH FOUND:
[Source] → [Node2] → [Node3] → ... → [Destination]

ROUTE DETAILS:
├─ Total Travel Cost: [X] units
├─ Nodes Explored: [N] nodes
└─ Path Length: [M] hops

SEQUENCE OF VISITED LOCATIONS:
1. [Location1]
2. [Location2]
...
N. [DestinationLocation]

═══════════════════════════════════════
```

---

### D. Implementation Architecture

#### Code Structure Requirements:

```python
# Required Functions

def build_graph(input_file):
    """
    Constructs adjacency list from input file.
    Returns: {node: [(neighbor, cost), ...], ...}
    """
    pass

def calculate_heuristic(current, goal, coordinates):
    """
    Computes admissible heuristic (Euclidean/Manhattan distance).
    Returns: float (estimated cost)
    """
    pass

def ida_star(graph, start, goal, heuristic_fn):
    """
    Core IDA* algorithm implementation.
    Returns: (path: list, cost: int, nodes_explored: int)
    """
    pass

def parse_input(filename):
    """Validates and parses input file."""
    pass

def write_output(filename, path, cost, explored, sequence):
    """Formats and writes output to specification."""
    pass

def main(input_file, output_file):
    """Orchestrates entire pipeline."""
    pass
```

#### Data Structure Choices:

| Component | Recommended | Rationale |
|-----------|-------------|-----------|
| Graph | Adjacency List | Memory efficient for sparse networks |
| Heuristic Lookup | Dictionary {node: coordinates} | O(1) access |
| Path Tracking | List/Deque | Preserve order for output |
| Priority Queue | heapq.heappush/pop | Fast min-extraction for frontier |
| Visited Set | Set {node_id} | O(1) membership testing |

---

## ⚙️ Implementation Constraints & Guidelines

### Mandatory Requirements

1. **Algorithm**: Use IDA* - no substitutes
2. **Graph Structure**: Implement proper adjacency representation
3. **Heuristic**: Admissible (Euclidean or Manhattan distance)
4. **Error Handling**: 
   - Empty graph detection
   - Unreachable destination handling
   - Invalid input validation
5. **Generalization**: Code must work for ANY input format (no hardcoding)
6. **Single File**: All code in one `.py` or `.ipynb` file

### Code Quality Standards

```python
# ✅ DO: Modular, well-commented, handles edge cases
def ida_star(graph, start, goal, heuristic_fn):
    """
    Performs Iterative Deepening A* search.
    
    Args:
        graph: Adjacency list {node: [(neighbor, cost)]}
        start: Starting node
        goal: Goal node
        heuristic_fn: Function h(node) → cost estimate
    
    Returns:
        (optimal_path: list, total_cost: int, nodes_explored: int)
    
    Raises:
        ValueError: If start or goal not in graph
        RuntimeError: If no path exists
    """
    if start not in graph:
        raise ValueError(f"Start node {start} not in graph")
    
    explored = set()
    depth_limit = heuristic_fn(start, goal)
    
    while True:
        result = _search(graph, start, goal, 0, depth_limit, 
                        heuristic_fn, explored)
        if result is not None:
            return result
        depth_limit = result  # Increase threshold
```

### ❌ Anti-Patterns to Avoid

- Hardcoded test cases mixed with algorithm logic
- Global variables for graph/state management
- Missing comments on algorithm steps
- Exception swallowing without logging
- Unvalidated user inputs
- Fragmented code across multiple files

---

## 📊 Evaluation Rubric (12 Marks Total)

### 1. Fully Executable Code (40% = 4.8 marks)
```
✓ All functionality working without errors
✓ Correct IDA* implementation
✓ Proper input/output file handling
✓ No crashes on valid/invalid inputs
✓ Output format exactly matches specification
```

### 2. Code Quality (25% = 3 marks)
```
✓ Modular design with clear function separation
✓ Comprehensive inline comments
✓ Proper error handling & validation
✓ Efficient data structure choices
✓ Readable variable/function naming
```

### 3. Design Document (20% = 2.4 marks)
```
✓ Complete PEAS analysis
✓ Heuristic strategy with admissibility proof
✓ IDA* algorithm explanation with example trace
✓ Alternate approach with performance comparison
✓ Technical accuracy within 4-page limit
```

### 4. Testing & Output Correctness (15% = 1.8 marks)
```
✓ Both test cases produce correct optimal paths
✓ Cost calculation accuracy
✓ Node exploration tracking correctness
✓ Output formatting compliance
✓ Edge case handling (unreachable nodes, etc.)
```

---

## ⏰ Submission Timeline & Penalties

### Late Submission Impact

| Submission Window | Penalty | Max Score |
|-------------------|---------|-----------|
| By June 8, 23:55 | 0 marks | 12/12 ✓ |
| June 8 23:56 - June 9 23:55 | -2 marks | 10/12 |
| June 9 23:56 - June 10 23:55 | -6 marks | 6/12 |
| After June 10 23:55 | No evaluation | 0/12 ✗ |

**Submission Method:**
- Platform: Taxila (NOT email, NOT GitHub, NOT other channels)
- Format: Single ZIP file with naming convention: `[GroupId]_A1_PS01_[YYYYMMDD].zip`
- Contents: All 6 required deliverables

---

## 🚨 Critical Success Factors

### Before Submission:

- [ ] **Read entire assignment document** - Multiple times
- [ ] **Plan group roles** - Assign clear responsibilities
- [ ] **Track contributions** - Update Excel sheet regularly (don't wait until end)
- [ ] **Test thoroughly** - Both provided test cases + edge cases
  - Single node graphs
  - Disconnected components
  - Circular paths
  - Large graphs (scalability)
- [ ] **Verify output format** - Character-perfect match to specification
- [ ] **Code review** - Peer review within group before submission
- [ ] **Design document** - Write clear, technical explanations
- [ ] **No plagiarism** - All original work (refer to institutional policy)

### Common Pitfalls (Avoid!):

❌ Confusing g(n) and h(n) values  
❌ Implementing A* instead of IDA*  
❌ Hardcoding test cases  
❌ Incorrect heuristic (not admissible)  
❌ Not tracking explored nodes  
❌ Fragmented code across files  
❌ Incorrect output format  
❌ No error handling for edge cases  
❌ Late submission after grace period  

---

## 📚 Learning Resources

### Primary Reference
- **Textbook:** *Artificial Intelligence: A Modern Approach (4th Edition)*
  - Authors: Peter Norvig & Stuart J. Russell
  - Chapters: Informed Search Strategies (Ch. 3-4), Heuristic Functions

### Key Concepts to Master
1. **Search Algorithms:** Breadth-first, Depth-first, A*, IDA*
2. **Heuristic Functions:** Admissibility, consistency, domination
3. **Graph Algorithms:** Dijkstra, shortest path, cost optimization
4. **Time/Space Complexity:** Analysis of search algorithms
5. **Python Implementation:** Data structures, heaps, generators

### Recommended Study Path
```
1. Understand problem → 2. Study IDA* theory → 3. Code prototype
→ 4. Test with test cases → 5. Optimize & document → 6. Design doc
```

---

## 🤝 Group Collaboration Guidelines

### Submission Rules
- **One submission per group** (no resubmissions allowed after deadline)
- **All deliverables** must be in single ZIP file
- **Contribution tracking** ensures fair assessment
- **Individual accountability** through design document defense potential

### Team Communication
- Use GitHub issues/discussions for clarifications (hints provided by instructors)
- Distribute code reviews and testing responsibilities
- Maintain regular progress tracking via contribution spreadsheet

---

## 📞 Support & Clarification

- **Platform:** Taxila discussion section (monitored by instructors)
- **Response Time:** Hints provided; direct solutions NOT given
- **Policy:** Read assignment completely before asking questions
- **Collaboration:** Discussions encouraged; plagiarism NOT tolerated

---

## ✨ Success Metrics Checklist

### Pre-Submission Quality Gates:

- [ ] **Functional:** Code runs without errors on both test cases
- [ ] **Optimal:** Paths match expected optimal solutions
- [ ] **Documented:** Every function has clear docstring
- [ ] **Tested:** Edge cases handled gracefully
- [ ] **Formatted:** Output exactly matches specification (character by character)
- [ ] **Designed:** 4-page design document completed with technical depth
- [ ] **Attributed:** Contribution sheet sums to 100% with accurate percentages
- [ ] **Packaged:** All files in correctly-named ZIP file
- [ ] **Verified:** Manual trace through IDA* execution for test case
- [ ] **Submitted:** Via Taxila before deadline with confirmation

---

## 📝 Final Notes

> **"The implementation is not just about code; it's about demonstrating your understanding of informed search algorithms, heuristic design, and problem-solving methodology."**

This assignment evaluates:
- ✅ Your ability to implement complex algorithms
- ✅ Your understanding of memory-efficient search strategies  
- ✅ Your software engineering practices (modularity, documentation)
- ✅ Your problem-solving approach (PEAS analysis, design thinking)

---

## 📌 Document Metadata

| Property | Value |
|----------|-------|
| **Version** | 2.0 (Enhanced) |
| **Last Updated** | May 31, 2026 |
| **Repository** | [SEM2_ACI_Assignment](https://github.com/vbhandeo-bits/SEM2_ACI_Assignment) |
| **Format** | Markdown with embedded specifications |
| **Purpose** | Comprehensive requirement capture for intelligent path-finding assignment |

---

**Good luck! Make this assignment AWESOME! 🚀**
