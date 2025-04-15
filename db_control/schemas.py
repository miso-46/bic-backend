from pydantic import BaseModel, Field
from typing import List, Union, Dict
from decimal import Decimal
import datetime
from typing import Optional

# 店舗ログイン情報
class StoreLoginRequest(BaseModel):
    name: str
    password: str

# レスポンスに店舗情報とキャラクター情報（メッセージやバイナリデータ）を含める
# characterフィールドには 'name', 'image', 'movie', 'voice_1', 'voice_2', 'message_1', 'message_2' を含む
# バイナリデータ（画像や音声など）はbase64エンコード済みの文字列にする想定
class CharacterInfo(BaseModel):
    name: str
    image: Optional[str]
    video: Optional[str]
    voice_1: Optional[str]
    voice_2: Optional[str]
    message_1: Optional[str]
    message_2: Optional[str]

class StoreLoginResponse(BaseModel):
    store_id: int
    store_name: str
    prefecture: str
    character: CharacterInfo

# ユーザー属性情報
class UserInfo(BaseModel):
    store_id: int
    category_id: int
    age: int
    gender: str
    household: int

    class Config:
        orm_mode = True

class UserInfoResponse(BaseModel):
    reception_id: int

# 回答データ（リクエスト用）
class Answer(BaseModel):
    questionId: int
    answer: int

# 回答リクエストのスキーマ
class AnswerRequest(BaseModel):
    receptionId: int
    answers: List[Answer]

# レスポンス用（オプション）
class AnswerResponse(BaseModel):
    message: str

# 回答候補のスキーマ
class Choice(BaseModel):
    label: str
    value: str

# 質問と回答候補（リクエスト用）
class QuestionWithChoices(BaseModel):
    id: int
    question_text: str
    answer_type: str
    choices: list[Choice] = []

# むかげん開発用範囲 ----
class UserAnswer(BaseModel):
    questionId: int
    value: int

class UserInput(BaseModel):
    receptionId: int
    answers: List[UserAnswer]

class ConfirmRecommendation(BaseModel):
    receptionId: int
    scores: Dict[int, float]  # metrics_id: score

class PriorityItem(BaseModel):
    reception_id: int
    metrics_id: int
    level: Decimal

class PriorityIn(BaseModel):
    priorities: List[PriorityItem]

class PriorityScore(BaseModel):
    metricsId: int
    name: str
    score: Decimal
# むかげん開発用範囲 ---- ここまで -----