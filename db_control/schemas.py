from pydantic import BaseModel, Field
from typing import List, Union
import datetime

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
    value: Union[int, bool, str]

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
