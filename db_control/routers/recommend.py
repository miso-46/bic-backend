from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from db_control.connect import get_db
from db_control import schemas, crud

router = APIRouter(prefix="/recommend",tags=["recommend"])

# --- 1. Pydanticモデル ---
class SurveyResponse(BaseModel):
    answers: Dict[str, str]  # 例: {"Q1": "選択肢A", "Q2": "選択肢B"}


# --- 2. 加重設定（質問と選択肢ごとの評価軸） ---
weight_map = {
    "Q1": {
        "選択肢A": {"主体性": 1.0},
        "選択肢B": {"主体性": 0.5, "協調性": 0.5}
    },
    "Q2": {
        "選択肢A": {"論理的思考": 1.0},
        "選択肢B": {"論理的思考": 0.5, "判断力": 0.5},
        "選択肢C": {"判断力": 1.0}
    },
    "Q3": {
        "選択肢A": {"協調性": 1.0},
        "選択肢B": {"主体性": 0.7, "協調性": 0.3}
    }
}


# --- 3. 製品ごとの特徴量（評価軸とスコア） ---
product_features = {
    "製品A": {"主体性": 0.8, "協調性": 0.6, "判断力": 0.4},
    "製品B": {"論理的思考": 0.9, "判断力": 0.7},
    "製品C": {"協調性": 0.8, "主体性": 0.5},
    "製品D": {"判断力": 1.0, "協調性": 0.3}
}


# --- 4. ユーザースコア計算 ---
def calculate_scores(answers: dict, weights: dict) -> dict:
    scores = {}
    for question_id, selected_option in answers.items():
        if question_id in weights and selected_option in weights[question_id]:
            for axis, weight in weights[question_id][selected_option].items():
                scores[axis] = scores.get(axis, 0) + weight
    return scores


# --- 5. 製品マッチング（スコア上位3件） ---
def match_products(user_scores: dict, product_features: dict, top_n: int = 3) -> List[Dict[str, float]]:
    product_scores = []
    for product, features in product_features.items():
        score = sum(user_scores.get(axis, 0) * weight for axis, weight in features.items())
        product_scores.append({"product": product, "score": round(score, 2)})
    return sorted(product_scores, key=lambda x: x["score"], reverse=True)[:top_n]


# --- 6. FastAPIエンドポイント ---
@router.post("", response_model=schemas.RecommendationResponse)
def recommend(answer_request: schemas.AnswerRequest, db: Session = Depends(get_db)):
    result = crud.recommend_products(db, answer_request)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result
