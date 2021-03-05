from typing import Optional
from fastapi import FastAPI, Depends
from db.definitions import DBSession
from db.interactions import get_topic, get_thread
from schema import TopicResponse, ThreadResponse

from sqlalchemy.orm import Session

app = FastAPI()

def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()

@app.get('/topics/{topic_id}', response_model=TopicResponse)
def read_topic(topic_id: int, db: Session = Depends(get_db)):
    response = TopicResponse(data=get_topic(db, topic_id))
    return response

@app.get('/threads/{thread_id}', response_model=ThreadResponse)
def read_thread(thread_id: int, db: Session = Depends(get_db)):
    response = ThreadResponse(data=get_thread(db, thread_id))
    return response