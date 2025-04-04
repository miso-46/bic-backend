from sqlalchemy.orm import Session
from db_control import models, schemas
import datetime

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


# 質問と回答候補を送る
def get_questions_by_category(db: Session, category_id: int):
    questions = db.query(models.Question).filter(models.Question.category_id == category_id).all()
    result = []

    for q in questions:
        if q.answer_type.value == "boolean":
            choices = [{"label": "はい", "value": "1"}, {"label": "いいえ", "value": "0"}]
        elif q.answer_type.value == "numeric":
            choices = [{"label": str(i), "value": str(i)} for i in range(1, 6)]
        elif q.answer_type.value == "categorical":
            if q.id == 1:
                choices = [{"label": "1R / 1K", "value": "1R / 1K"},
                           {"label": "1DK〜2LDK", "value": "1DK〜2LDK"},
                           {"label": "3LDK以上", "value": "3LDK以上"}]
            elif q.id == 4:
                choices = [{"label": "エリア設定", "value": "エリア設定"},
                           {"label": "スケジュール設定", "value": "スケジュール設定"},
                           {"label": "どちらも", "value": "どちらも"},
                           {"label": "特になし", "value": "特になし"}]
            else:
                choices = []
        else:
            choices = []

        result.append({
            "id": q.id,
            "question_text": q.question_text,
            "answer_type": q.answer_type.value,
            "choices": choices
        })

    return result


# ユーザー属性情報登録
def save_user_info(db: Session, user_info: schemas.UserInfo) -> int:
    new_user = models.User(
        store_id=5,  # フロントエンドから固定で送られる store_id（今は一旦5にしておく）
        age=user_info.age,
        gender=user_info.gender,
        household=user_info.household,
        time=datetime.datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user.id