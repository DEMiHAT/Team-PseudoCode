from ml_models.bkt import BayesianKnowledgeTracer, Skill

engine = BayesianKnowledgeTracer()

skill = Skill.STACK_CONCEPTUAL

attempts = [True, True, False, True, True, True, True]

print("\n========== BKT STUDENT MASTERY DEMO ==========")
print(f"Skill: {skill.value}")
print(f"Initial Mastery: {engine.get_mastery(skill) * 100:.2f}%")

for number, answer in enumerate(attempts, start=1):

    result = engine.update_skill(skill, answer)

    status = "Correct" if answer else "Incorrect"

    print(
        f"Attempt {number} | "
        f"Answer: {status:<9} | "
        f"Mastery: {result.mastery_percentage:6.2f}% | "
        f"Mastered: {result.is_mastered}"
    )

print("==============================================")