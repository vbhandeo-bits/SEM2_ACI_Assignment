# Smart Waste Collection Agent - Assignment 1 (PS1)

**Course:** Artificial Intelligence and Computational Intelligence  
**Weightage:** 12%  
**Deadline:** June 8, 2026, 11:55 PM IST

---

## 📋 Project Overview

This assignment implements an **intelligent path-finding system** for a Smart Waste Collection Robot Agent operating in Bengaluru's waste management network. The robot must determine optimal routes between waste collection centers and processing plants while minimizing operational costs using the **IDA\* (Iterative Deepening A\*) algorithm**.

### Problem Context

The Municipal Smart City initiative requires efficient waste collection and route optimization across multiple waste processing zones. The robot operates under:
- **Limited battery power and fuel efficiency constraints**
- **Weighted graph representation** of the city's waste management network
- **User-specified source and destination locations**
- **Need for cost-optimal route planning**

---

## 🎯 Key Requirements

### 1. **Problem Modeling - PEAS Analysis**
- **Performance Measure:** Minimize total travel cost (distance/fuel consumption)
- **Environment:** Weighted graph representing city waste network
- **Actuators:** Movement along connected roads
- **Sensors:** Current location, road network information

### 2. **Algorithm Selection: IDA\***

The assignment mandates the use of **Iterative Deepening A\*** (IDA*) for intelligent path-finding because:
- Combines depth-first search's memory efficiency with A\*'s optimality guarantee
- Eliminates heuristic-based overestimation issues
- Ideal for cost-optimal solutions with limited resources

### 3. **Required Analysis**

#### Heuristic Strategy
- **Heuristic Type:** Straight-line distance (Euclidean) OR Manhattan distance
- **Justification:** Provides admissible lower bound on actual cost without overestimating
- **Implementation:** Based on geographical coordinates of waste collection centers

#### Cost Function
- **g(n):** Actual cost from source to current node (road network weights)
- **h(n):** Estimated cost from current node to destination (heuristic)
- **f(n) = g(n) + h(n):** Total estimated cost

---

## 📁 Deliverables Checklist

### Required Files:
- ✅ **designPS01_[GroupId].pdf** - Technical design document (max 4 pages)
  - PEAS analysis
  - Heuristic explanation and justification
  - IDA* algorithm explanation
  - One alternate modeling approach with performance analysis
  
- ✅ **[GroupId]_Contribution.xlsx** - Group contribution breakdown
  - Columns: Student Registration Number | Name | Percentage Contribution (%)
  
- ✅ **inputPS01.txt** - Test case input file
  - Format: Location definitions, road connections, source, destination
  
- ✅ **outputPS01.txt** - Algorithm execution output
  - Optimal path
  - Total travel cost
  - Number of nodes explored
  - Sequence of visited locations
  
- ✅ **solution.py** - Single Python notebook/file
  - Complete, modular, well-documented code
  - No fragmented files
  
- ✅ **[GroupId]_A1_PS01_XXXXXXXXXX.zip** - Final submission package

---

## 📊 Test Cases

### **Case 1: Bengaluru Waste Network**
```
Locations: 6
Roads: 7

Road Network:
MG_Road ↔ Electronic_City (cost: 2)
MG_Road ↔ Koramangala (cost: 4)
Electronic_City ↔ Whitefield (cost: 2)
Whitefield ↔ Yelahanka (cost: 4)
Whitefield ↔ Jayanagar (cost: 6)
Jayanagar ↔ Yelahanka (cost: 2)
Koramangala ↔ Hebbal (cost: 3)
Hebbal ↔ Yelahanka (cost: 5)

Source: MG_Road
Destination: Yelahanka
```

### **Case 2: Generic Graph**
```
Locations: 5
Roads: 6

Road Network:
A ↔ B (cost: 3)
A ↔ C (cost: 2)
B ↔ D (cost: 4)
C ↔ D (cost: 1)
C ↔ E (cost: 7)
D ↔ E (cost: 2)

Source: A
Destination: E
```

---

## 🔍 Expected Algorithm Output

For each test case, the algorithm must print:

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

## ⚙️ Implementation Requirements

### Code Structure:
- **Modular Design:** Separate functions for graph construction, heuristic calculation, IDA* search
- **Error Handling:** Validate inputs, handle invalid paths, catch edge cases
- **Data Structures:** Adjacency list/matrix for graph, priority queues for node management
- **Documentation:** Comprehensive comments explaining algorithm logic and data flow

### Input File Format (inputPS01.txt):
```
6
7
MG_Road Electronic_City 2
MG_Road Koramangala 4
Electronic_City Whitefield 2
Whitefield Yelahanka 4
Whitefield Jayanagar 6
Jayanagar Yelahanka 2
Koramangala Hebbal 3
Hebbal Yelahanka 5
MG_Road
Yelahanka
```

### Output File Format (outputPS01.txt):
```
OPTIMAL_PATH: MG_Road → Electronic_City → Whitefield → Yelahanka
TOTAL_COST: 8
NODES_EXPLORED: 12
VISITED_SEQUENCE: [MG_Road, Electronic_City, Whitefield, Yelahanka]
```

---

## 📋 Evaluation Criteria (12 Marks)

| Criterion | Weight |
|-----------|--------|
| **Fully Executable Code** | 40% |
| - All functionality working as expected | - |
| - Correct algorithm implementation | - |
| - Proper input/output handling | - |
| **Code Quality** | 25% |
| - Well-structured and modular | - |
| - Comprehensive comments | - |
| - Error handling | - |
| **Design Document** | 20% |
| - PEAS analysis | - |
| - Heuristic justification | - |
| - Alternate approach analysis | - |
| - Technical accuracy (max 4 pages) | - |
| **Testing & Output Correctness** | 15% |
| - Accurate path finding | - |
| - Correct cost calculation | - |
| - Node exploration tracking | - |

---

## ⚠️ Critical Instructions

1. **Compulsory:** Use IDA* algorithm and proper graph data structures
2. **Error Handling:** Implement checks for empty/full data structures and invalid inputs
3. **No Hardcoding:** Make code generic for any input file format
4. **Single File:** All code in one Python notebook/file (no fragmentation)
5. **No Plagiarism:** Original work only (refer to institutional policy)
6. **Compilation:** Code with errors will receive maximum 25% of marks

---

## 📌 Late Submission Penalty

| Submission Window | Penalty | Evaluation |
|-------------------|---------|------------|
| By June 8, 11:55 PM | 0 marks deducted | Full marks possible (12M) |
| June 8 11:56 PM - June 9 11:55 PM | -2 marks | Max 10 marks |
| June 9 11:56 PM - June 10 11:55 PM | -6 marks | Max 6 marks |
| After June 10 11:55 PM | No evaluation | 0 marks |

---

## 📚 Reference Materials

- **Textbook:** Artificial Intelligence: A Modern Approach (4th Edition)
  - Authors: Peter Norvig & Stuart J. Russell
  - Topics: Informed Search Strategies, Heuristic Functions, IDA*

---

## 🤝 Group Submission

- **One submission per group** (No resubmissions allowed)
- **All deliverables in single ZIP file**
- **Naming Convention:** `[GroupId]_A1_PS01_XXXXXXXXXX.zip`
  - Example: `G026_A1_PS01_20260531.zip`
- **Submission Method:** Taxila > Assignment Section
  - **NOT** via email or other channels

---

## 📝 Notes for Success

- ✨ Read the entire assignment document carefully
- ✨ Plan group responsibilities and track contributions in Excel
- ✨ Test code thoroughly with both provided test cases
- ✨ Write a comprehensive design document with clear explanations
- ✨ Ensure all output formats strictly match specifications
- ✨ Use the discussion section for clarifications (only hints provided)

---

**Last Updated:** May 31, 2026  
**Repository:** [SEM2_ACI_Assignment](https://github.com/vbhandeo-bits/SEM2_ACI_Assignment)
