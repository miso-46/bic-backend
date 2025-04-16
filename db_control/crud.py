from sqlalchemy.orm import Session
from db_control import models, schemas
import datetime
import bcrypt
import os
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from dotenv import load_dotenv

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


# 店舗認証処理
def verify_store_credentials(db: Session, name: str, password: str):
    try:
        load_dotenv()
        account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
        container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

        store = db.query(models.Store).filter(models.Store.name == name).first()
        if not store or not bcrypt.checkpw(password.encode("utf-8"), store.password.encode("utf-8")):
            return None

        bic_girl = db.query(models.BicGirl).filter(models.BicGirl.store_id == store.id).first()
        if not bic_girl:
            return {
                "store_id": store.id,
                "store_name": store.name,
                "prefecture": store.prefecture,
                "character": schemas.CharacterInfo(
                    name="",
                    image=None,
                    video=None,
                    voice_1=None,
                    voice_2=None,
                    message_1=None,
                    message_2=None
                )
            }

        blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=account_key)

        def generate_sas_url(blob_name):
            if not blob_name:
                return None
            try:
                sas_token = generate_blob_sas(
                    account_name=account_name,
                    container_name=container_name,
                    blob_name=blob_name,
                    account_key=account_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
                )
                return f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
            except Exception:
                return None

        character = {
            "name": bic_girl.name,
            "image": generate_sas_url(bic_girl.image),
            "video": generate_sas_url(bic_girl.video),
            "voice_1": generate_sas_url(bic_girl.voice_1),
            "voice_2": generate_sas_url(bic_girl.voice_2),
            "message_1": bic_girl.message_1,
            "message_2": bic_girl.message_2,
        }

        return {
            "store_id": store.id,
            "store_name": store.name,
            "prefecture": store.prefecture,
            "character": character
        }
    except Exception as e:
        return {"error": f"認証エラー: {str(e)}"}

# 店舗タブレット登録
from sqlalchemy.orm import Session
from db_control import models, schemas

def create_tablet(db: Session, tablet: schemas.TabletRegisterRequest):
    db_tablet = models.Tablet(
        uuid=tablet.uuid,
        store_id=tablet.store_id,
        floor=tablet.floor,
        area=tablet.area,
    )
    db.add(db_tablet)
    db.commit()
    db.refresh(db_tablet)
    return db_tablet


# 店員呼び出し
def get_reception_info_for_call(db: Session, reception_id: int, uuid: str):
    try:
        reception = db.query(models.Reception).filter(models.Reception.id == reception_id).first()
        if not reception:
            raise ValueError("指定されたreception_idが存在しません")

        user = db.query(models.User).filter(models.User.id == reception.user_id).first()
        if not user:
            raise ValueError("Receptionに紐づくユーザーが存在しません")

        store = db.query(models.Store).filter(models.Store.id == user.store_id).first()
        if not store:
            raise ValueError("ユーザーに紐づく店舗が存在しません")

        category = db.query(models.Category).filter(models.Category.id == reception.category_id).first()
        if not category:
            raise ValueError("Receptionに紐づくカテゴリが存在しません")

        tablet = db.query(models.Tablet).filter(models.Tablet.uuid == uuid).first()
        if not tablet:
            raise ValueError("指定されたUUIDのタブレット情報が存在しません")

        return {
            "store_name": store.name,
            "floor": tablet.floor if tablet else "未登録",
            "area": tablet.area if tablet else "未登録",
            "category_name": category.name
        }
    except Exception as e:
        raise e  # ここで詳細なエラー内容をそのまま上に投げる
