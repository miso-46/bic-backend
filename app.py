from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db_control import models, schemas, crud, connect
from db_control.routers import login, tablet, answers, question, user_info, recommend, priority, call_sales, store
import os
from dotenv import load_dotenv

app = FastAPI()

# 環境変数の読み込み
load_dotenv()
# フロントエンドのURLを環境変数から取得
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")  # デフォルトをローカル開発環境に設定

# CORSの設定 フロントエンドからの接続を許可する部分
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],  # 許可するオリジン
    allow_credentials=True, # Cookie や認証情報を許可
    allow_methods=["*"], # すべてのHTTPメソッド（GET, POST, PUT, DELETEなど）を許可
    allow_headers=["*"] # すべてのHTTPヘッダーを許可
)

# DB初期化
models.Base.metadata.create_all(bind=connect.engine)

# ルーターを追加
app.include_router(login.router)
app.include_router(tablet.router)
app.include_router(answers.router)
app.include_router(question.router)
app.include_router(user_info.router)
app.include_router(recommend.router)
app.include_router(priority.router)
app.include_router(call_sales.router)
app.include_router(store.router)

@app.get("/")
def root():
    return {"message": "Hello World"}