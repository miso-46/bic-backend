from pydantic import BaseModel, Field
from typing import List, Union
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
class AnswerRequest(BaseModel):
    answers: Dict[str, str]  # 例: {"Q1": "選択肢A", "Q2": "選択肢B"}

class Recommendation(BaseModel):
    product: str
    score: float

class RecommendationResponse(BaseModel):
    user_scores: Dict[str, float]
    recommendations: List[Recommendation]  
