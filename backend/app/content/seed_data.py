"""
Seed data module for initial IT22301 curriculum, benchmark problems, and default learner.
"""

import json
from sqlalchemy.orm import Session
from app.models.learner import Learner
from app.models.concept import Concept
from app.models.problem import Problem
from app.models.knowledge_state import KnowledgeState
from app.content.curriculum import IT22301_CURRICULUM
from app.core.logging import logger


def seed_initial_content(db: Session) -> None:
    """Populates database with initial curriculum concepts and starter problems."""
    # Check if concepts already exist
    if db.query(Concept).first() is not None:
        logger.info("Database already contains seed concepts. Skipping seed.")
        return

    logger.info("Populating initial IT22301 curriculum concepts...")
    concepts_map = {}

    for unit in IT22301_CURRICULUM:
        category = unit["category"]
        for c_data in unit["concepts"]:
            concept = Concept(
                code=c_data["code"],
                name=c_data["name"],
                category=category,
                description=c_data["description"],
                order_index=c_data["order_index"],
            )
            db.add(concept)
            db.flush()
            concepts_map[c_data["code"]] = concept

    # Seed Default Undergraduate Learner for local development
    default_learner = Learner(
        student_id="22IT001",
        full_name="Arjun Patel",
        email="arjun.patel@engineering.edu",
        semester=3,
    )
    db.add(default_learner)
    db.flush()

    # Seed Knowledge States with standard prior (P(L_0) = 0.20)
    for concept in concepts_map.values():
        k_state = KnowledgeState(
            learner_id=default_learner.id,
            concept_id=concept.id,
            p_known=0.20,
            p_learn=0.15,
            p_guess=0.15,
            p_slip=0.10,
        )
        db.add(k_state)

    # Seed Benchmark Problems
    sll_concept = concepts_map.get("IT22301-U1-SLL")
    if sll_concept:
        sll_problem = Problem(
            concept_id=sll_concept.id,
            title="Reverse a Singly Linked List",
            slug="reverse-singly-linked-list",
            difficulty="Easy",
            description_md=(
                "### Problem Statement\n\n"
                "Given the head of a singly linked list, reverse the list in-place and return the reversed list's head.\n\n"
                "#### Constraints\n"
                "- Number of nodes: `[0, 5000]`\n"
                "- Node value: `-5000 <= Node.val <= 5000`\n"
                "- Must run in **O(N)** time and **O(1)** auxiliary space."
            ),
            starter_code_java=(
                "/**\n"
                " * Definition for singly-linked list node:\n"
                " * public class ListNode {\n"
                " *     int val;\n"
                " *     ListNode next;\n"
                " *     ListNode(int val) { this.val = val; }\n"
                " * }\n"
                " */\n"
                "class Solution {\n"
                "    public ListNode reverseList(ListNode head) {\n"
                "        // TODO: Implement in-place linked list reversal\n"
                "        ListNode prev = null;\n"
                "        ListNode current = head;\n"
                "        \n"
                "        while (current != null) {\n"
                "            // Your pointer manipulation here\n"
                "        }\n"
                "        \n"
                "        return prev;\n"
                "    }\n"
                "}\n"
            ),
            driver_code_java="",
            test_cases_json=json.dumps([
                {"id": 1, "input": "[1,2,3,4,5]", "expected": "[5,4,3,2,1]", "is_hidden": False, "explanation": "Standard 5-node list reversal"},
                {"id": 2, "input": "[1,2]", "expected": "[2,1]", "is_hidden": False, "explanation": "Two-element list reversal"},
                {"id": 3, "input": "[]", "expected": "[]", "is_hidden": False, "explanation": "Empty list boundary case"},
                {"id": 4, "input": "[42]", "expected": "[42]", "is_hidden": True, "explanation": "Single element preservation"},
            ]),
            is_active=True,
        )
        db.add(sll_problem)

    stk_concept = concepts_map.get("IT22301-U2-STK")
    if stk_concept:
        stk_problem = Problem(
            concept_id=stk_concept.id,
            title="Valid Parentheses Evaluation",
            slug="valid-parentheses",
            difficulty="Easy",
            description_md=(
                "### Problem Statement\n\n"
                "Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, determine if the input string is valid.\n\n"
                "An input string is valid if:\n"
                "1. Open brackets must be closed by the same type of brackets.\n"
                "2. Open brackets must be closed in the correct order.\n"
                "3. Every close bracket has a corresponding open bracket of the same type."
            ),
            starter_code_java=(
                "import java.util.Stack;\n\n"
                "class Solution {\n"
                "    public boolean isValid(String s) {\n"
                "        Stack<Character> stack = new Stack<>();\n"
                "        \n"
                "        for (char c : s.toCharArray()) {\n"
                "            // TODO: Match brackets using stack ADT\n"
                "        }\n"
                "        \n"
                "        return stack.isEmpty();\n"
                "    }\n"
                "}\n"
            ),
            driver_code_java="",
            test_cases_json=json.dumps([
                {"id": 1, "input": "\"()\"", "expected": "true", "is_hidden": False, "explanation": "Simple balanced pair"},
                {"id": 2, "input": "\"()[]{}\"", "expected": "true", "is_hidden": False, "explanation": "Sequential balanced pairs"},
                {"id": 3, "input": "\"(]\"", "expected": "false", "is_hidden": False, "explanation": "Mismatched closing bracket"},
                {"id": 4, "input": "\"]\"", "expected": "false", "is_hidden": True, "explanation": "Unmatched closing bracket with empty stack"},
            ]),
            is_active=True,
        )
        db.add(stk_problem)

    bst_concept = concepts_map.get("IT22301-U3-BST")
    if bst_concept:
        bst_problem = Problem(
            concept_id=bst_concept.id,
            title="Search in a Binary Search Tree",
            slug="search-in-bst",
            difficulty="Easy",
            description_md=(
                "### Problem Statement\n\n"
                "You are given the `root` of a binary search tree (BST) and an integer `val`.\n\n"
                "Find the node in the BST that the node's value equals `val` and return the subtree rooted with that node. "
                "If such a node does not exist, return `null`."
            ),
            starter_code_java=(
                "/**\n"
                " * Definition for a binary tree node:\n"
                " * public class TreeNode {\n"
                " *     int val;\n"
                " *     TreeNode left;\n"
                " *     TreeNode right;\n"
                " *     TreeNode(int val) { this.val = val; }\n"
                " * }\n"
                " */\n"
                "class Solution {\n"
                "    public TreeNode searchBST(TreeNode root, int val) {\n"
                "        // TODO: Implement recursive or iterative BST search\n"
                "        if (root == null || root.val == val) {\n"
                "            return root;\n"
                "        }\n"
                "        \n"
                "        return null;\n"
                "    }\n"
                "}\n"
            ),
            driver_code_java="",
            test_cases_json=json.dumps([
                {"id": 1, "input": "root = [4,2,7,1,3], val = 2", "expected": "[2,1,3]", "is_hidden": False, "explanation": "Target present in left subtree"},
                {"id": 2, "input": "root = [4,2,7,1,3], val = 5", "expected": "[]", "is_hidden": False, "explanation": "Target absent from BST"},
            ]),
            is_active=True,
        )
        db.add(bst_problem)

    db.commit()
    logger.info("Curriculum concepts, default student, and benchmark problems seeded successfully.")
