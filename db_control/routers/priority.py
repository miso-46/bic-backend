from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from db_control import schemas, models
from db_control.connect import get_db
from typing import List


router = APIRouter(prefix="/priority", tags=["priority"])

@router.post("")
def save_priorities(data: schemas.PriorityIn, db: Session = Depends(get_db)):
    for item in data.priorities:
        priority = models.Priority(
            reception_id=item.reception_id,
            metrics_id=item.metrics_id,
            level=item.level
        )
        db.add(priority)

    db.commit()
    return {"message": "saved"}

@router.get("/{reception_id}", response_model=List[schemas.PriorityScore])
def get_priority_scores(reception_id: int, db: Session = Depends(get_db)):
    results = (
        db.query(
            models.Priority.metrics_id,
            models.Metric.name,
            models.Priority.level
        )
        .join(models.Metric, models.Priority.metrics_id == models.Metric.id)
        .filter(models.Priority.reception_id == reception_id)
        .all()
    )

    return [
        schemas.PriorityScore(
            metricsId=metrics_id,
            name=name,
            score=level
        ) for metrics_id, name, level in results
    ]