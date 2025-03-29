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
