from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db_control.connect import get_db
from db_control import models, crud
from typing import List

router = APIRouter(prefix="/question", tags=["question"])

# 辞書でquestion_idごとに選択肢を定義（ハードコーディング） 将来的にはDB管理したい
question_choices = {
    1: ["1R / 1K", "1DK〜2LDK", "3LDK以上"],
    2: ["はい", "いいえ"],
    3: ["はい", "いいえ"],
    4: ["エリア設定", "スケジュール設定", "どちらも", "特になし"],
    5: ["はい", "いいえ"],
    6: ["はい", "いいえ"],
    7: ["1", "2", "3", "4", "5"],
    8: ["1", "2", "3", "4", "5"],
    9: ["1", "2", "3", "4", "5"],
    10: ["1", "2", "3", "4", "5"],
    11: ["1", "2", "3", "4", "5"],
    12: ["1", "2", "3", "4", "5"],
}

@router.get("/{category_id}")
def get_questions(category_id: int, db: Session = Depends(get_db)):
    result = crud.get_questions_by_category(db, category_id)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result