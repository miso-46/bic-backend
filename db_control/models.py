# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, DateTime, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum
import datetime

# Baseクラスを作成
Base = declarative_base()

# user テーブル（ユーザー属性）
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, nullable=True)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)  # 'male', 'female', 'other' などを想定
    household = Column(Integer, nullable=False)
    time = Column(DateTime, default=datetime.datetime.utcnow)


# storeテーブル
class Store(Base):
    __tablename__ = "store"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)  # bcryptでハッシュ化済みの文字列を格納
    prefecture = Column(String(100), nullable=True)
    is_available = Column(Boolean, default=True)
    time = Column(DateTime, default=datetime.datetime.utcnow)


# bic_girl テーブル（店舗キャラクター情報）
class BicGirl(Base):
    __tablename__ = "bic_girl"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    store_id = Column(Integer, ForeignKey("store.id"), nullable=True)
    image = Column(String(255), nullable=True)
    movie = Column(String(255), nullable=True)
    voice_1 = Column(String(255), nullable=True)
    voice_2 = Column(String(255), nullable=True)
    message_1 = Column(String(255), nullable=True)
    message_2 = Column(String(255), nullable=True)

# reception テーブル（ユーザーと質問セッションを紐づけ）
class Reception(Base):
    __tablename__ = "reception"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    category_id = Column(Integer, nullable=False)
    time = Column(DateTime, default=datetime.datetime.utcnow)


# answer_info テーブル（回答を格納）
class AnswerInfo(Base):
    __tablename__ = "answer_info"
    id = Column(Integer, primary_key=True, index=True)
    reception_id = Column(Integer, ForeignKey("reception.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("question.id"), nullable=False)
    answer = Column(Integer, nullable=False)

# ---  むかげん開発用コード ---
# question テーブル（設問情報）
class Question(Base):
    __tablename__ = "question"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("category.id"))
    question_text = Column(String)

# question_option テーブル（設問の選択肢情報）
class QuestionOption(Base):
    __tablename__ = "question_option"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("question.id"))
    label = Column(String)
    value = Column(Integer)

# suggestion テーブル（お薦めした商品の情報を格納）
class Suggestion(Base):
    __tablename__ = "suggestion"
    id = Column(Integer, primary_key=True, index=True)
    reception_id = Column(Integer, ForeignKey("reception.id"))
    product_id = Column(Integer, ForeignKey("product.id"))
    ranking = Column(Integer)

# product テーブル（商品の基礎情報）
class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    brand = Column(String)
    price = Column(Integer)
    width = Column(Float)
    depth = Column(Float)
    height = Column(Float)
    description = Column(String)
    category_id = Column(Integer, ForeignKey("category.id"))

# metrics テーブル（商品の評価項目）
class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer)
    name = Column(String)

# metrics テーブル（ユーザーごとの評価結果）
class Priority(Base):
    __tablename__ = "priority"
    id = Column(Integer, primary_key=True, index=True)
    reception_id = Column(Integer, ForeignKey("reception.id"))
    metrics_id = Column(Integer, ForeignKey("metrics.id"))
    level = Column(Numeric(10, 2))
# ---  むかげん開発用コード ここまで ---