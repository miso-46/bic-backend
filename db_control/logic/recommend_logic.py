from typing import Dict, List
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from db_control.schemas import UserInput
from db_control import models
import numpy as np
import pandas as pd
import time
from dotenv import load_dotenv
import os
import datetime
from azure.storage.blob import generate_blob_sas, BlobSasPermissions

def convert_answers_to_scores(user_input: UserInput, base_score=4.5, step=0.25) -> Dict[int, float]:
    scores = {i: base_score for i in range(1, 10)}
    for ans in user_input.answers:
        qid, val = ans.questionId, ans.value
        if qid == 1:
            if val == 0: scores[1] += step
            elif val == 1: scores[5] += step
        elif qid == 2 and val == 1:
            scores[4] += step
        elif qid == 4 and val == 0:
            scores[6] += step
        elif qid == 5 and val == 0:
            scores[3] += step
        elif qid == 7:
            if val == 0: scores[1] += step
            elif val == 1: scores[9] += step
        elif qid == 8:
            if val == 0: scores[2] += step
            elif val == 1: scores[5] += step
        elif qid == 9 and val == 0:
            scores[1] += step
        elif qid == 10 and val == 0:
            scores[6] += step
            scores[9] -= step
        elif qid == 11 and val == 0:
            scores[7] += step
            scores[8] += step
    return scores

def calculate_similarity(product_df, user_scores: Dict[int, float]) -> List[tuple]:
    distances = []
    for pid in product_df["product_id"].unique():
        pdata = product_df[product_df["product_id"] == pid]
        distance = 0
        for _, row in pdata.iterrows():
            mid = row["metrics_id"]
            if mid in user_scores:
                distance += (user_scores[mid] - row["level"]) ** 2
        distances.append((pid, np.sqrt(distance)))
    distances.sort(key=lambda x: x[1])
    return distances

def get_top_products(user_scores: Dict[int, float], db: Session, top_n=3) -> List[int]:
    df = pd.read_sql("SELECT product_id, metrics_id, level FROM product_metrics", db.bind)
    similarities = calculate_similarity(df, user_scores)
    return [int(pid) for pid, _ in similarities[:top_n]]

# recommend商品を保存
def save_suggestions(reception_id: int, product_ids: List[int], db: Session, max_retries: int = 3):
    retries = 0
    while retries < max_retries:
        try:
            # 既存レコード削除
            db.query(models.Suggestion).filter(models.Suggestion.reception_id == reception_id).delete()

            # Suggestion オブジェクト作成
            suggestions = [
                models.Suggestion(reception_id=reception_id, product_id=pid, ranking=rank)
                for rank, pid in enumerate(product_ids, start=1)
            ]

            db.bulk_save_objects(suggestions)
            db.commit()
            return  # 成功したら終了

        except OperationalError as e:
            if "Deadlock found" in str(e):
                db.rollback()
                retries += 1
                time.sleep(0.5)  # リトライ前に少し待機
            else:
                db.rollback()
                raise  # その他のエラーはそのまま上へ

    # すべてのリトライで失敗した場合
    raise Exception(f"Deadlock could not be resolved after {max_retries} retries.")

# recommend商品の詳細とスコアの取得
def get_product_details(product_ids: List[int], reception_id: int, db: Session):
    ids_str = "(" + ",".join(map(str, product_ids)) + ")"

    # Blob SAS URL生成用環境変数読み込み
    load_dotenv()
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    def generate_sas_url(blob_name: str):
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

    # 商品情報の取得
    query = f"""
        SELECT
            p.id,
            p.name,
            p.brand,
            p.price,
            p.width,
            p.depth,
            p.height,
            p.description,
            p.image AS image,
            c.name AS category
        FROM product p
        LEFT JOIN category c ON p.category_id = c.id
        WHERE p.id IN {ids_str}
    """
    df = pd.read_sql(query, db.bind)

    # 商品ごとの metrics スコアを取得（metrics_id を使うように修正）
    score_query = f"""
        SELECT
            pm.product_id,
            pm.metrics_id,
            pm.level
        FROM product_metrics pm
        WHERE pm.product_id IN {ids_str}
    """
    score_df = pd.read_sql(score_query, db.bind)

    # 商品IDごとのスコア辞書に変換（← metrics_id を key に）
    score_dict = (
        score_df.groupby("product_id")
        .apply(lambda x: {str(row["metrics_id"]): row["level"] for _, row in x.iterrows()})
        .to_dict()
    )

    # 商品詳細とスコア統合
    return [
        {
            "id": int(row["id"]),
            "name": row["name"],
            "brand": row["brand"],
            "price": row["price"],
            "dimensions": {
                "width": row["width"],
                "depth": row["depth"],
                "height": row["height"]
            },
            "description": row["description"],
            "image": generate_sas_url(row["image"]),
            "category": row["category"],
            "scores": score_dict.get(row["id"], {})  # ← RadarChart 用にここで渡す！
        }
        for _, row in df.iterrows()
    ]