from dataclasses import dataclass
from app.config import settings

@dataclass(frozen=True)
class BKTParameters:
    initial: float = settings.bkt_initial
    transition: float = settings.bkt_transition
    guess: float = settings.bkt_guess
    slip: float = settings.bkt_slip

def update(prior: float, correct: bool, params: BKTParameters = BKTParameters()) -> float:
    if not 0 <= prior <= 1: raise ValueError("prior must be between 0 and 1")
    if correct:
        denominator = prior * (1 - params.slip) + (1 - prior) * params.guess
        posterior = prior * (1 - params.slip) / denominator
    else:
        denominator = prior * params.slip + (1 - prior) * (1 - params.guess)
        posterior = prior * params.slip / denominator
    return posterior + (1 - posterior) * params.transition
