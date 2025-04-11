from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db_control.connect import get_db
from db_control import schemas, crud

router = APIRouter(prefix="/answers",tags=["answers"])

@router.post("", response_model=schemas.AnswerResponse)
def submit_answers(answer_request: schemas.AnswerRequest, db: Session = Depends(get_db)):
    result = crud.save_answers(db, answer_request)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

@router.get("/{reception_id}", response_model=schemas.AnswerRequest)
def read_answers(reception_id: int, db: Session = Depends(get_db)):
    result = crud.get_answers_by_reception_id(db, reception_id)
    if not result.answers:
        raise HTTPException(status_code=404, detail="回答が見つかりません")
    return result