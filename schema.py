from pydantic import BaseModel
from typing import Optional, Literal, List, Tuple
from datetime import datetime


class DBTopic(BaseModel):
    id: int
    user_id: int
    title: Optional[str] = None

    class Config:
        orm_mode = True


class DBThread(BaseModel):
    id: int
    user_id: int
    title: Optional[str] = None
    is_vegan: bool = False

    class Config:
        orm_mode = True


class DBPost(BaseModel):
    id: int
    user_id: int
    text: Optional[str]
    parent_id: int

    class Config:
        orm_mode = True


class DBUser(BaseModel):
    id: int
    name: str
    password_hash: str
    password_salt: str
    token: Optional[str]
    token_expires_at: Optional[datetime]

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class PathElement(BaseModel):
    id: int
    title: Optional[str]


Path = List[PathElement]


class TopicData(BaseModel):
    title: Optional[str]
    link: int
    numTopics: Optional[int]
    numThreads: Optional[int]
    lastPost: Optional[str]
    user: User


class ThreadData(BaseModel):
    title: Optional[str]
    link: int
    numPosts: Optional[int]
    lastPost: Optional[str]
    isVegan: bool
    user: User


class Topic(BaseModel):
    title: Optional[str] = None
    topics: List[TopicData]
    threads: List[ThreadData]
    user: User
    path: Path


class TopicResponse(BaseModel):
    type: Literal['topic'] = 'topic'
    data: Topic


class PostData(BaseModel):
    user: User
    text: Optional[str]
    id: int


class Thread(BaseModel):
    title: Optional[str]
    posts: List[PostData]
    path: Path


class ThreadResponse(BaseModel):
    type: Literal['thread'] = 'thread'
    data: Thread


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal['bearer'] = 'bearer'


class Error(BaseModel):
    detail: str
