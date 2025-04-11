from pydantic import BaseModel, Field
from typing import Dict,List, Union
import datetime

# 回答データ（リクエスト用）
class Answer(BaseModel):
    questionId: int
    value: Union[int, float, bool, str]

# 回答リクエストのスキーマ
class AnswerRequest(BaseModel):
    receptionId: int
    answers: List[Answer]

# レスポンス用（オプション）
class AnswerResponse(BaseModel):
    message: str

# むかげん開発用範囲
class UserAnswer(BaseModel):
    questionId: int
    value: int

class UserInput(BaseModel):
    receptionId: int
    answers: List[UserAnswer]

class ConfirmRecommendation(BaseModel):
    receptionId: int
    scores: Dict[int, float]  # metrics_id: score