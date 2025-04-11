from typing import Dict, List
from sqlalchemy.orm import Session
from db_control.schemas import UserInput
from db_control import models

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
    import numpy as np
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
    import pandas as pd
    df = pd.read_sql("SELECT product_id, metrics_id, level FROM product_metrics", db.bind)
    similarities = calculate_similarity(df, user_scores)
    return [int(pid) for pid, _ in similarities[:top_n]]

def save_suggestions(reception_id: int, product_ids: List[int], db: Session):
    from db_control.models import Suggestion
    db.query(Suggestion).filter(Suggestion.reception_id == reception_id).delete()
    for rank, pid in enumerate(product_ids, start=1):
        db.add(Suggestion(reception_id=reception_id, product_id=pid, ranking=rank))
    db.commit()

def get_product_details(product_ids: List[int], db: Session):
    import pandas as pd
    ids_str = "(" + ",".join(map(str, product_ids)) + ")"
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
            c.name AS category
        FROM product p
        LEFT JOIN category c ON p.category_id = c.id
        WHERE p.id IN {ids_str}
    """
    df = pd.read_sql(query, db.bind)
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
            "category": row["category"]
        }
        for _, row in df.iterrows()
    ]