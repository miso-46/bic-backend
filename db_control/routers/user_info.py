from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db_control.connect import get_db
from db_control import schemas, crud

router = APIRouter(prefix="/user-info", tags=["user"])

from db_control.schemas import UserInfo

@router.post("", response_model=int)
def save_user_info(user_info: UserInfo, db: Session = Depends(get_db)):
    try:
        return crud.save_user_info(db, user_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))