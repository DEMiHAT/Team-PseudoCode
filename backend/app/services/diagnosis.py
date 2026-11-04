from app.models import Attempt, Problem

def diagnose(attempt: Attempt, problem: Problem) -> dict:
    output = (attempt.compiler_output or "").lower()
    failed = [r for r in attempt.results if not r.get("passed")]
    if "compile" in output or "cannot find symbol" in output or "';' expected" in output:
        return _result("Compilation error", attempt.compiler_output or "Compiler rejected the program.", .98, "Review Java syntax and the compiler location.")
    if "time limit" in output:
        return _result("Time complexity issue", "Execution exceeded the configured limit.", .92, "Reconsider the algorithm's asymptotic complexity.")
    if "exception" in output or "runtime" in output:
        return _result("Logical error", attempt.compiler_output or "The program raised a runtime error.", .88, "Trace values immediately before the failing operation.")
    boundary = any(str(r.get("input", "")).strip() in {"[]", "0", "1", ""} for r in failed)
    if boundary:
        return _result("Boundary condition error", "An empty or smallest-size case failed.", .84, "Check initialization, loop bounds, and empty inputs.")
    if failed:
        return _result("Incorrect condition", f"{len(failed)} evaluated case(s) produced an incorrect result.", .72, "Trace the branch conditions with a failing visible case.")
    return _result("Conceptual misunderstanding", "Repeated unsuccessful attempts without a more specific deterministic signal.", .55, f"Revisit the core invariant for {problem.title}.")

def _result(category, evidence, confidence, response):
    return {"category": category, "evidence": evidence[:2000], "confidence": confidence, "recommended_response": response}
