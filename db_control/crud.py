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
