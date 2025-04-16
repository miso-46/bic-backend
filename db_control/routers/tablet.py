from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db_control.connect import get_db
from db_control import schemas, crud

router = APIRouter(prefix="/tablet", tags=["tablet"])

@router.post("/register", response_model=schemas.TabletRegisterResponse)
def tablet_register(request: schemas.TabletRegisterRequest, db: Session = Depends(get_db)):
    db_tablet = crud.create_tablet(db, request)
    return schemas.TabletRegisterResponse(message="タブレット情報を登録しました")
