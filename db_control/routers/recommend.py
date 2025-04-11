from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from db_control import schemas, models
from db_control.connect import get_db
from db_control.logic.recommend_logic import (
    convert_answers_to_scores,
    get_top_products,
    save_suggestions,
    get_product_details
)

router = APIRouter(prefix="/recommend", tags=["recommend"])

# ステップ① スコア計算
@router.post("/score")
def recommend_score(user_input: schemas.UserInput, db: Session = Depends(get_db)):
    user_scores = convert_answers_to_scores(user_input)
    sorted_scores = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)

    # metrics.name を取りに行く
    metric_ids = [mid for mid, _ in sorted_scores]
    metrics = db.query(models.Metric).filter(models.Metric.id.in_(metric_ids)).all()
    metric_id_to_name = {metric.id: metric.name for metric in metrics}

    return JSONResponse(content={
        "receptionId": user_input.receptionId,
        "priorities": [
            {
                "metricsId": mid,
                "name": metric_id_to_name.get(mid, f"Metric-{mid}"),
                "score": round(score, 2)
            }
            for mid, score in sorted_scores
        ]
    })


# ステップ② 推薦確定
@router.post("/confirm")
def confirm_recommendation(
    confirm_input: schemas.ConfirmRecommendation,
    db: Session = Depends(get_db)
):
    top_product_ids = get_top_products(confirm_input.scores, db)
    save_suggestions(confirm_input.receptionId, top_product_ids, db)
    product_details = get_product_details(top_product_ids, db)

    return JSONResponse(content={
        "receptionId": confirm_input.receptionId,
        "recommendedProducts": product_details
    })