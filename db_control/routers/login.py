from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db_control.connect import get_db
from db_control import schemas, crud

router = APIRouter(prefix="/login", tags=["login"])

@router.post("", response_model=schemas.StoreLoginResponse)
def store_login(request: schemas.StoreLoginRequest, db: Session = Depends(get_db)):
    store_info = crud.verify_store_credentials(db, request.name, request.password)
    if not store_info:
        raise HTTPException(status_code=401, detail="店舗名またはパスワードが正しくありません。")

    character_data = store_info.pop("character", {})
    return schemas.StoreLoginResponse(
        **store_info,
        character=schemas.CharacterInfo(**character_data)
    )