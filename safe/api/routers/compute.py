from fastapi import APIRouter

from safe.api.schemas import PredictabilityRequest, PredictabilityResponse
from safe.logic.predictability import art_predictability, predictability_rating

router = APIRouter(prefix="/compute", tags=["Compute"])


@router.post("/predictability", response_model=PredictabilityResponse)
def compute_predictability(body: PredictabilityRequest):
    pairs = [(t.actual_business_value, t.planned_business_value) for t in body.teams]
    score = art_predictability(pairs)
    return PredictabilityResponse(score_pct=score, rating=predictability_rating(score))
