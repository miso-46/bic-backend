from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db_control.connect import get_db
from db_control import crud, schemas
from typing import List

router = APIRouter(prefix="/store", tags=["store"])

@router.get("/{store_id}", response_model=schemas.StoreLoginResponse)
def get_store(store_id: int, db: Session = Depends(get_db)):
    store_info = crud.get_store_info(db, store_id)
    if not store_info:
        raise HTTPException(status_code=401, detail="store_idが正しくありません")

    character_data = store_info.pop("character", {})
    return schemas.StoreLoginResponse(
        **store_info,
        character=schemas.CharacterInfo(**character_data)
    )