from sqlalchemy.orm import Session
from db_control import models, schemas

# 回答をDBに保存
def save_answers(db: Session, answer_request: schemas.AnswerRequest):
    # reception_id が存在するか確認
    reception = db.query(models.Reception).filter(models.Reception.id == answer_request.receptionId).first()
    if not reception:
        return {"error": "Invalid reception ID"}

    for answer in answer_request.answers:
        # question の型を取得
        question = db.query(models.Question).filter(models.Question.id == answer.questionId).first()
        if not question:
            return {"error": f"Invalid question ID: {answer.questionId}"}

        answer_type = question.answer_type.value  # Enumの値を取得

        # 回答データを適切なカラムに格納
        answer_data = models.AnswerInfo(
            reception_id=answer_request.receptionId,
            question_id=answer.questionId,
            answer_numeric=answer.value if answer_type == "numeric" else None,
            answer_boolean=answer.value if answer_type == "boolean" else None,
            answer_categorical=answer.value if answer_type == "categorical" else None
        )

        db.add(answer_data)

    db.commit()
    return {"message": "Answers saved successfully"}

# ---  むかげん開発用コード  ---
def get_weight_map(db: Session):
    result = db.query(QuestionWeight).all()
    weight_map = {}
    for row in result:
        weight_map.setdefault(row.question_id, {}).setdefault(row.choice_label, {})[row.axis] = row.weight
    return weight_map

def get_product_features(db: Session):
    result = db.query(ProductFeature).all()
    product_features = {}
    for row in result:
        product_features.setdefault(row.product_name, {})[row.axis] = row.weight
    return product_features

def calculate_scores(answers: dict, weights: dict) -> dict:
    scores = {}
    for question_id, selected_option in answers.items():
        if question_id in weights and selected_option in weights[question_id]:
            for axis, weight in weights[question_id][selected_option].items():
                scores[axis] = scores.get(axis, 0) + weight
    return scores

def match_products(user_scores: dict, product_features: dict, top_n: int = 3):
    product_scores = []
    for product, features in product_features.items():
        score = sum(user_scores.get(axis, 0) * weight for axis, weight in features.items())
        product_scores.append({"product": product, "score": round(score, 2)})
    return sorted(product_scores, key=lambda x: x["score"], reverse=True)[:top_n]

def recommend_products(db: Session, answer_request):
    weight_map = get_weight_map(db)
    product_features = get_product_features(db)
    user_scores = calculate_scores(answer_request.answers, weight_map)
    recommendations = match_products(user_scores, product_features)
    return {
        "user_scores": user_scores,
        "recommendations": recommendations
    }