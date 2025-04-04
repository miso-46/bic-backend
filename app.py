from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db_control import models, schemas, crud, connect
from db_control.routers import answers
from db_control.routers import question
import os
from dotenv import load_dotenv

# MySQLに繋いだらコメントアウト外す
# # MySQLのテーブル作成
# from db_control.create_tables import init_db

# # アプリケーション初期化時にテーブルを作成
# init_db()

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
app.include_router(answers.router)
app.include_router(question.router)

@app.get("/")
def root():
    return {"message": "Hello World"}