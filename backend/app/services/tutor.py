import httpx
from app.config import settings

SYSTEM = """You are PALS, a careful DSA tutor. Follow the provided scaffold level. Never claim code is correct, alter mastery, contradict the diagnosis, reveal hidden tests, or provide a full solution below L5. Be concise and ask the learner to think."""

async def tutor_response(context: dict) -> tuple[str, bool]:
    prompt = SYSTEM + "\n\nVerified learning context:\n" + "\n".join(f"{k}: {v}" for k, v in context.items())
    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(f"{settings.ollama_base_url}/api/generate", json={"model": settings.ollama_model, "prompt": prompt, "stream": False})
            response.raise_for_status(); text = response.json().get("response", "").strip()
            if text: return text, False
    except (httpx.HTTPError, KeyError): pass
    level = int(context.get("scaffold_level", 1))
    concept = context.get("concept", "this concept")
    diagnosis = context.get("diagnosis", "the last attempt")
    fallbacks = {
        0: f"Try another {concept} problem independently. State the invariant before coding.",
        1: f"Small hint: for {concept}, what must remain true after every iteration?",
        2: f"Recall the core invariant for {concept}. Relate it to: {diagnosis}.",
        3: f"Trace one small input by hand. At each step, write the active index and the value that changes. Where does {diagnosis} first appear?",
        4: f"Break the algorithm into initialization, repeated update, and termination. Focus first on the condition implicated by {diagnosis}.",
        5: f"Walkthrough: define the invariant, initialize it for the smallest input, update it once per step, then verify the boundary and termination conditions. Apply each stage to {concept} before translating it to Java.",
    }
    return fallbacks.get(level, fallbacks[1]), True
