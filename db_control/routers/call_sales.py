from fastapi import APIRouter, Depends, HTTPException
from db_control.connect import get_db
from db_control import crud, schemas
from sqlalchemy.orm import Session
import os
import json
import requests
import traceback

router = APIRouter(prefix="/call_sales",tags=["call_sales"])

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")  # .env に記載

@router.post("", response_model=schemas.CallSalesResponse)
def call_sales(request: schemas.CallSalesRequest, db: Session = Depends(get_db)):
    try:
        if not SLACK_WEBHOOK_URL:
            raise HTTPException(status_code=500, detail="SLACK_WEBHOOK_URL is not set")

        try:
            data = crud.get_reception_info_for_call(db, request.reception_id, request.uuid)
        except ValueError as ve:
            raise HTTPException(status_code=404, detail=str(ve))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"内部エラー: {str(e)}")

        headers = {"Content-Type": "application/json"}
        payload = {
            "username": data["store_name"],
            "attachments": [
                {
                    "fallback": f"{data['store_name']}で店員呼び出しがあります",
                    "pretext": "*📣 店員呼び出し*",
                    "color": "#36a64f",
                    "fields": [
                        {
                            "title": "タブレット場所",
                            "value": f"{data['floor']}、{data['area']}",
                            "short": False
                        },
                        {
                            "title": "家電カテゴリ",
                            "value": data["category_name"],
                            "short": False
                        },  # <-- this comma is added
                        {
                            "title": "接客画面リンク",
                            "value": f"<{request.frontend_url}>",
                            "short": False
                        }
                    ]
                }
            ]
        }

        response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
        print("Slack response:", response.status_code, response.text)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Slack通知に失敗しました: {response.text}")

        # Slack通知に成功したらテーブルに記録
        from db_control import models
        sales_call_record = models.SalesCall(reception_id=request.reception_id)
        db.add(sales_call_record)
        db.commit()

        return {"message": "テスト通知を送信しました"}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except HTTPException:
        raise  # 明示的に再スロー
    except Exception as e:
        print("==== エラー発生 ====")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"内部エラー: {str(e)}")
