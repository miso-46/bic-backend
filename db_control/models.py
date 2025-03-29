# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum
import datetime

# Baseクラスを作成
Base = declarative_base()

# 回答の型を定義
class AnswerType(enum.Enum):
    numeric = "numeric"
    boolean = "boolean"
    categorical = "categorical"

# reception テーブル（ユーザーと質問セッションを紐づけ）
class Reception(Base):
    __tablename__ = "reception"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    category_id = Column(Integer, nullable=False)
    time = Column(DateTime, default=datetime.datetime.utcnow)

# question テーブル（設問情報）
class Question(Base):
    __tablename__ = "question"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, nullable=False)
    question_text = Column(String, nullable=False)
    answer_type = Column(Enum(AnswerType), nullable=False)

# answer_info テーブル（回答を格納）
class AnswerInfo(Base):
    __tablename__ = "answer_info"
    id = Column(Integer, primary_key=True, index=True)
    reception_id = Column(Integer, ForeignKey("reception.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("question.id"), nullable=False)
    answer_numeric = Column(Integer, nullable=True)
    answer_boolean = Column(Boolean, nullable=True)
    answer_categorical = Column(String, nullable=True)