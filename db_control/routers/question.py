from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db_control.connect import get_db
from db_control import models, crud
from typing import List

router = APIRouter(prefix="/question", tags=["question"])

@router.get("/{category_id}")
def get_questions(category_id: int, db: Session = Depends(get_db)):
    result = crud.get_questions_by_category(db, category_id)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result