"""
Master API v1 Router.
Aggregates modular routes for health, concepts, problems, execution, tutoring, and learners.
"""

from fastapi import APIRouter
from app.routes.health_routes import router as health_router
from app.routes.concept_routes import router as concept_router
from app.routes.problem_routes import router as problem_router
from app.routes.execution_routes import router as execution_router
from app.routes.tutoring_routes import router as tutoring_router
from app.routes.learner_routes import router as learner_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router, tags=["System Health"])
api_v1_router.include_router(concept_router, prefix="/concepts", tags=["IT22301 Curriculum Concepts"])
api_v1_router.include_router(problem_router, prefix="/problems", tags=["DSA Coding Problems"])
api_v1_router.include_router(execution_router, prefix="/execution", tags=["Judge0 Code Execution"])
api_v1_router.include_router(tutoring_router, prefix="/tutoring", tags=["Adaptive Tutoring & Scaffolding"])
api_v1_router.include_router(learner_router, prefix="/learners", tags=["Learner Knowledge States"])

