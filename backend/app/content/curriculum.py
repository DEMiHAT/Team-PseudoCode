"""
IT22301 – Data Structures and Algorithms curriculum structure.
Defines the official syllabus breakdown for undergraduate engineering students.
"""

IT22301_CURRICULUM = [
    {
        "unit": 1,
        "name": "Linear Data Structures - List Implementations",
        "category": "Linear Collections",
        "concepts": [
            {
                "code": "IT22301-U1-ARR",
                "name": "Dynamic Arrays and Resizing",
                "description": "Amortized complexity, memory layout, insert/delete operations, and in-place shifting.",
                "order_index": 1,
            },
            {
                "code": "IT22301-U1-SLL",
                "name": "Singly Linked Lists",
                "description": "Pointer manipulation, head/tail sentinels, reversal, cycle detection (Floyd's algorithm).",
                "order_index": 2,
            },
            {
                "code": "IT22301-U1-DLL",
                "name": "Doubly Linked Lists",
                "description": "Bidirectional traversals, symmetric pointer updates, memory overhead, and node deletion.",
                "order_index": 3,
            },
        ],
    },
    {
        "unit": 2,
        "name": "Linear Data Structures - Stacks and Queues",
        "category": "Linear ADTs",
        "concepts": [
            {
                "code": "IT22301-U2-STK",
                "name": "Stack ADT and Applications",
                "description": "LIFO mechanics, parenthesis matching, postfix expression evaluation, and call-stack simulation.",
                "order_index": 4,
            },
            {
                "code": "IT22301-U2-QUE",
                "name": "Queue ADT and Circular Queues",
                "description": "FIFO mechanics, circular array buffer arithmetic (modulo indexing), and double-ended queues (Deque).",
                "order_index": 5,
            },
        ],
    },
    {
        "unit": 3,
        "name": "Non-Linear Data Structures - Trees",
        "category": "Hierarchical Structures",
        "concepts": [
            {
                "code": "IT22301-U3-BST",
                "name": "Binary Search Trees (BST)",
                "description": "BST property, search, in-order/pre-order/post-order traversals, and node deletion cases.",
                "order_index": 6,
            },
            {
                "code": "IT22301-U3-AVL",
                "name": "Self-Balancing Trees (AVL)",
                "description": "Balance factor invariants, single and double rotations (LL, RR, LR, RL), height guarantees.",
                "order_index": 7,
            },
            {
                "code": "IT22301-U3-HEP",
                "name": "Binary Heaps and Priority Queues",
                "description": "Max/Min heap property, array representation, siftUp/siftDown, and heapsort.",
                "order_index": 8,
            },
        ],
    },
    {
        "unit": 4,
        "name": "Non-Linear Data Structures - Graphs",
        "category": "Graph Algorithms",
        "concepts": [
            {
                "code": "IT22301-U4-GRP",
                "name": "Graph Representations and Traversals",
                "description": "Adjacency matrix vs list, Breadth-First Search (BFS), Depth-First Search (DFS), cycle detection.",
                "order_index": 9,
            },
            {
                "code": "IT22301-U4-SPT",
                "name": "Shortest Paths and Minimum Spanning Trees",
                "description": "Dijkstra's greedy shortest path, Prim's and Kruskal's MST algorithms.",
                "order_index": 10,
            },
        ],
    },
]
