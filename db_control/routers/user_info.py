from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db_control import schemas, crud
from db_control.connect import get_db

router = APIRouter(prefix="/user_info", tags=["user_info"])

@router.post("", response_model=schemas.UserInfoResponse)  # ← ここで指定
def create_user(user_info: schemas.UserInfo, db: Session = Depends(get_db)):
    result = crud.save_user_info(db, user_info)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result