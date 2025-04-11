from sqlalchemy.orm import Session
from db_control import models, schemas
import datetime

# 回答をDBに保存
def save_answers(db: Session, answer_request: schemas.AnswerRequest):
    try:
        for answer in answer_request.answers:
            # question の型を取得
            question = db.query(models.Question).filter(models.Question.id == answer.questionId).first()
            if not question:
                return {"error": f"Invalid question ID: {answer.questionId}"}
            # 回答データを適切なカラムに格納
            answer_data = models.AnswerInfo(
            reception_id=answer_request.receptionId,
                question_id=answer.questionId,
                answer=answer.answer
            )
            db.add(answer_data)
        db.commit()
        return {"message": "保存が完了しました"}
    except Exception as e:
        db.rollback()
        return {"error": f"回答の保存に失敗しました: {str(e)}"}


# 質問と回答候補を取得して送信する
def get_questions_by_category(db: Session, category_id: int):
    # 指定カテゴリの質問を取得
    questions = db.query(models.Question).filter(models.Question.category_id == category_id).all()
    # 全選択肢を取得して、question_id ごとにまとめる
    option_rows = db.query(models.QuestionOption).all()
    option_map = {}
    for opt in option_rows:
        if opt.question_id not in option_map:
            option_map[opt.question_id] = []
        option_map[opt.question_id].append({
            "label": opt.label,
            "value": opt.value
        })
    # レスポンス構築
    result = {}
    for q in questions:
        choices = option_map.get(q.id, [])  # 選択肢がある場合のみ使う
        result[str(q.id)] = {
            "question_text": q.question_text,
            "options": choices
        }
    return result


# ユーザー属性情報登録
def save_user_info(db: Session, user_info: schemas.UserInfo):
    try:
        new_user = models.User(
            store_id=user_info.store_id,
            age=user_info.age,
            gender=user_info.gender,
            household=user_info.household,
            time=datetime.datetime.utcnow()
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        new_reception = models.Reception(
            user_id=new_user.id,
            category_id=user_info.category_id,
            time=datetime.datetime.utcnow()
        )
        db.add(new_reception)
        db.commit()
        db.refresh(new_reception)

        return {"reception_id": new_reception.id}
    except Exception as e:
        db.rollback()
        return {"error": f"ユーザー情報の保存に失敗しました: {str(e)}"}
    
# ---  むかげん開発用コード  ---
# 回答をDBから取得
def get_answers_by_reception_id(db: Session, reception_id: int) -> schemas.AnswerRequest:
    answer_records = (
        db.query(models.AnswerInfo)
        .filter(models.AnswerInfo.reception_id == reception_id)
        .all()
    )
    answer_list = [
        schemas.Answer(
            questionId=record.question_id,
            answer=record.answer
        )
        for record in answer_records
    ]
    return schemas.AnswerRequest(
        receptionId=reception_id,
        answers=answer_list
    )

# ほげほげ
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
# ---  むかげん開発用コード ここまで ---