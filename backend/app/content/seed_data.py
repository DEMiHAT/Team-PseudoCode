"""
Seed data module for curriculum structures, topics, prerequisites, and activities.
Does NOT fabricate student performance data.
"""

import json
from sqlalchemy.orm import Session
from app.models.subject import Subject
from app.models.unit import Unit
from app.models.topic import Topic
from app.models.prerequisite import Prerequisite
from app.models.activity import Activity
from app.content.curriculum import IT22301_CURRICULUM
from app.core.logging import logger


def seed_initial_content(db: Session) -> None:
    """
    Populates structural curriculum content: Subjects, Units, Topics, Prerequisites, and Activities.
    Does NOT create fake student attempts or performance data.
    """
    # Check if subjects already exist
    if db.query(Subject).first() is not None:
        logger.info("Curriculum structure already seeded. Skipping.")
        return

    logger.info("Seeding IT22301 and multi-subject curriculum architecture...")

    # 1. Seed Primary Subject: IT22301
    dsa_subject = Subject(
        code="IT22301",
        name="Data Structures and Algorithms",
        description="Undergraduate core course covering linear, hierarchical, and graph data structures.",
        is_active=True,
    )
    db.add(dsa_subject)

    # 2. Seed Secondary Subject: CS22302 (demonstrating multi-subject architecture)
    discrete_math = Subject(
        code="CS22302",
        name="Discrete Mathematical Structures",
        description="Sets, relations, recurrence relations, and graph theoretical fundamentals.",
        is_active=True,
    )
    db.add(discrete_math)
    db.flush()

    topics_map = {}

    # 3. Seed Units and Topics for IT22301
    for unit_data in IT22301_CURRICULUM:
        unit_obj = Unit(
            subject_id=dsa_subject.id,
            unit_number=unit_data["unit"],
            title=f"Unit {unit_data['unit']}: {unit_data['name']}",
            description=unit_data["category"],
            order_index=unit_data["unit"],
        )
        db.add(unit_obj)
        db.flush()

        for topic_data in unit_data["concepts"]:
            topic_obj = Topic(
                unit_id=unit_obj.id,
                code=topic_data["code"],
                name=topic_data["name"],
                description=topic_data["description"],
                difficulty_level="Intermediate",
                order_index=topic_data["order_index"],
            )
            db.add(topic_obj)
            db.flush()
            topics_map[topic_data["code"]] = topic_obj

    # 4. Seed Prerequisite DAG Relationships
    # Singly Linked List (U1-SLL) is prerequisite for Doubly Linked List (U1-DLL)
    sll_topic = topics_map.get("IT22301-U1-SLL")
    dll_topic = topics_map.get("IT22301-U1-DLL")
    if sll_topic and dll_topic:
        db.add(Prerequisite(topic_id=dll_topic.id, prerequisite_topic_id=sll_topic.id, strength=1.0, is_mandatory=True))

    # Binary Search Tree (U3-BST) is prerequisite for AVL Trees (U3-AVL)
    bst_topic = topics_map.get("IT22301-U3-BST")
    avl_topic = topics_map.get("IT22301-U3-AVL")
    if bst_topic and avl_topic:
        db.add(Prerequisite(topic_id=avl_topic.id, prerequisite_topic_id=bst_topic.id, strength=1.0, is_mandatory=True))

    # 5. Seed Benchmark Activities (Coding Exercises)
    if sll_topic:
        reverse_sll_activity = Activity(
            topic_id=sll_topic.id,
            title="Reverse a Singly Linked List",
            slug="reverse-singly-linked-list",
            activity_type="coding_exercise",
            difficulty="Easy",
            description_md=(
                "Given the head of a singly linked list, reverse the list in-place and return the reversed list's head.\n\n"
                "**Constraints:** O(N) time and O(1) space."
            ),
            starter_template=(
                "class Solution {\n"
                "    public ListNode reverseList(ListNode head) {\n"
                "        ListNode prev = null;\n"
                "        ListNode current = head;\n"
                "        while (current != null) {\n"
                "            ListNode next = current.next;\n"
                "            current.next = prev;\n"
                "            prev = current;\n"
                "            current = next;\n"
                "        }\n"
                "        return prev;\n"
                "    }\n"
                "}\n"
            ),
            solution_reference="",
            test_cases_json=json.dumps([
                {"id": 1, "input": "[1,2,3,4,5]", "expected": "[5,4,3,2,1]", "is_hidden": False},
                {"id": 2, "input": "[]", "expected": "[]", "is_hidden": False},
                {"id": 3, "input": "[42]", "expected": "[42]", "is_hidden": True},
            ]),
            is_active=True,
        )
        db.add(reverse_sll_activity)

    stk_topic = topics_map.get("IT22301-U2-STK")
    if stk_topic:
        parentheses_activity = Activity(
            topic_id=stk_topic.id,
            title="Valid Parentheses Evaluation",
            slug="valid-parentheses",
            activity_type="coding_exercise",
            difficulty="Easy",
            description_md=(
                "Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, "
                "determine if the input string is valid.\n\n"
                "An input string is valid if:\n"
                "1. Open brackets must be closed by the same type of brackets.\n"
                "2. Open brackets must be closed in the correct order (LIFO).\n"
                "3. Every close bracket has a corresponding open bracket of the same type."
            ),
            starter_template=(
                "import java.util.Scanner;\n"
                "import java.util.Stack;\n\n"
                "public class Main {\n"
                "    public static boolean isValid(String s) {\n"
                "        Stack<Character> stack = new Stack<>();\n"
                "        // TODO: Implement LIFO bracket validation\n"
                "        return stack.isEmpty();\n"
                "    }\n\n"
                "    public static void main(String[] args) {\n"
                "        Scanner scanner = new Scanner(System.in);\n"
                "        if (scanner.hasNextLine()) {\n"
                "            String input = scanner.nextLine().trim();\n"
                "            System.out.println(isValid(input));\n"
                "        }\n"
                "    }\n"
                "}\n"
            ),
            solution_reference=(
                "import java.util.Scanner;\n"
                "import java.util.Stack;\n\n"
                "public class Main {\n"
                "    public static boolean isValid(String s) {\n"
                "        Stack<Character> stack = new Stack<>();\n"
                "        for (char c : s.toCharArray()) {\n"
                "            if (c == '(' || c == '{' || c == '[') {\n"
                "                stack.push(c);\n"
                "            } else {\n"
                "                if (stack.isEmpty()) return false;\n"
                "                char top = stack.pop();\n"
                "                if (c == ')' && top != '(') return false;\n"
                "                if (c == '}' && top != '{') return false;\n"
                "                if (c == ']' && top != '[') return false;\n"
                "            }\n"
                "        }\n"
                "        return stack.isEmpty();\n"
                "    }\n\n"
                "    public static void main(String[] args) {\n"
                "        Scanner scanner = new Scanner(System.in);\n"
                "        if (scanner.hasNextLine()) {\n"
                "            String input = scanner.nextLine().trim();\n"
                "            System.out.println(isValid(input));\n"
                "        }\n"
                "    }\n"
                "}\n"
            ),
            test_cases_json=json.dumps([
                {"id": 1, "input": "()", "expected": "true", "is_hidden": False},
                {"id": 2, "input": "()[]{}", "expected": "true", "is_hidden": False},
                {"id": 3, "input": "(]", "expected": "false", "is_hidden": False},
                {"id": 4, "input": "([)]", "expected": "false", "is_hidden": False},
                {"id": 5, "input": "{[]}", "expected": "true", "is_hidden": False},
            ]),
            is_active=True,
        )
        db.add(parentheses_activity)

    db.commit()
    logger.info("Curriculum structure seeded successfully with zero fabricated student performance.")
