#!/usr/bin/python3

"""
A module to configure SQL alchemy and create tables
"""

from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sys import argv

user_name = argv[1]
password = argv[2]
db_name = argv[4]
host = argv[3]
db_url = "mysql+mysqldb://{}:{}@{}/{}".format(user_name, password, host, db_name)


engine = create_engine(db_url, echo=True, pool_pre_ping=True)
Base = declarative_base()

class Users(Base):
    """defines attribues for the User Class"""
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    gender = Column(String(50))
    date_of_birth = Column(Date)
    email = Column(String(100))
    email_verified = Column(Boolean, nullable=False, server_default="0")
    user_password = Column(String(255), nullable=False, server_default="")
    is_active = Column(Boolean, nullable=False, server_default="0")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated_at = Column(DateTime, default=datetime.utcnow)
    next_update = Column(DateTime, default=datetime.utcnow)
    user_name = Column(String(50), nullable=False, unique=True)
    bio = Column(Text)
    longitude = Column(Float)
    latitude = Column(Float)
    age = Column(Integer)
    profile_pic_path = Column(String(500))
    verification_code = Column(Integer)

class User_preferences(Base):
    """defines attribues for the User_preferences Class"""
    __tablename__ = "User_preferences"
    preferences_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(Users.id), unique=True)
    min_age = Column(Integer)
    max_age = Column(Integer)
    distance = Column(Integer)
    gender = Column(String(200))
    intentions = Column(String(200))
class Likes(Base):
    """defines attribues for the Likes Class"""
    __tablename__ = "Likes"
    like_id = Column(Integer, primary_key=True, autoincrement=True)
    user_1_id = Column(Integer, ForeignKey(Users.id))
    user_2_id = Column(Integer, ForeignKey(Users.id))
    is_matched = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
class Matches(Base):
    """defines attribues for the Matches Class"""
    __tablename__ = "Matches"
    match_id = Column(Integer, primary_key=True, autoincrement=True)
    user_1_id = Column(Integer, ForeignKey(Users.id))
    user_2_id = Column(Integer, ForeignKey(Users.id))
    user_1_notified = Column(Boolean)
    user_2_notified = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
class Messages(Base):
    """defines attribues for the Messages Class"""
    __tablename__ = "Messages"
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey(Users.id))
    receiver_id = Column(Integer, ForeignKey(Users.id))
    content = Column(Text)
    sent_at = Column(DateTime, default=datetime.utcnow)

class User_pics(Base):
    """defines attribues for the User_pics Class"""
    __tablename__ = "User_pics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(500))
    path = Column(String(500))
    user_id = Column(Integer, ForeignKey(Users.id))

Base.metadata.create_all(engine)
