from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.validation.scenarios import get_all_scenarios, get_scenario_by_id
from app.validation.evaluator import evaluate_all_scenarios
from app.analytics.ml_model import train_incident_classifier

router = APIRouter(prefix="/validation", tags=["Validation & Replay Lab"])


@router.get("/scenarios")
def list_scenarios():
    """Returns the 8 synthetic labeled scenarios defined in SRS Section 9."""
    return get_all_scenarios()


@router.get("/scenarios/{scenario_id}")
def get_scenario(scenario_id: str):
    sc = get_scenario_by_id(scenario_id)
    if not sc:
        raise HTTPException(status_code=404, detail="Scenario not found.")
    return sc


@router.get("/metrics")
def get_validation_metrics():
    """
    Computes and returns full operational metrics:
    - Lead Time (hours)
    - Sensitivity & PPV
    - False Alarms per 30 days
    - Benchmark against Naive Heat-Only Baseline
    - Signal Ablation table
    """
    return evaluate_all_scenarios()


@router.post("/train-ml")
def retrain_ml_model(db: Session = Depends(get_db)):
    """Triggers retraining of the supervised Logistic Regression classifier."""
    res = train_incident_classifier(db)
    return res

