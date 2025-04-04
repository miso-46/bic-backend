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
