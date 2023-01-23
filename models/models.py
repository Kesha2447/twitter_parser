# -*- coding: utf-8 -*-
'''Models for FastAPI'''

from enum import Enum
from typing import List, Dict
from pydantic import BaseModel


class BaseResponse(BaseModel):
    status: int


#users_info
class SessionInfo(BaseModel):
    session_id: int
    queue: int


class NewSessionResponse(BaseResponse):
    data: SessionInfo


#status
class StatusName(str, Enum):
    pending = "pending"
    success = "success"
    failed = "failed"


class Status(BaseModel):
    username: str
    status: str


class StatusResponse(BaseResponse):
    data: List[Status]


#user
class UserInfo(BaseModel):
    twitter_id: int
    name: str
    username: str
    following_count: int
    followers_count: int
    description: str


class UserInfoResponse(BaseResponse):
    data: UserInfo


#tweets
class TweetsResponse(BaseResponse):
    data: List[Dict]


#errors
class Error(BaseModel):
    code: int
    message: str


class ErrorResponse(BaseResponse):
    errors: List[Error]