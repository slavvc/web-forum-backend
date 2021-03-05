from pydantic import BaseModel
from typing import Optional, Literal

class Topic(BaseModel):
    id: int
    title: Optional[str] = None
    num_topics: Optional[int] = None
    num_threads: Optional[int] = None
    last_post: Optional[str] = None
    class Config():
        orm_mode = True

class TopicResponse(BaseModel):
    type: Literal['topic'] = 'topic'
    data: Topic

class Thread(BaseModel):
    id: int
    title: Optional[str] = None
    num_posts: Optional[int] = None
    last_post: Optional[str] = None
    is_vegan: bool = False
    class Config():
        orm_mode = True

class ThreadResponse(BaseModel):
    type: Literal['thread'] = 'thread'
    data: Thread