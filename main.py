from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from db.definitions import DBSession
from db_interactions import get_topic, get_thread, get_user_by_name, get_user_by_token
from db_interactions import user_exists, add_user, init_db, set_user_token, thread_exists
from db_interactions import add_post, post_belongs_to_user, remove_post
from utils import password_is_good, check_password
from schema import TopicResponse, ThreadResponse, User, TokenResponse

from sqlalchemy.orm import Session

init_db()

app = FastAPI()

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/api/authenticate')


def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()


def require_user(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)):
    user = get_user_by_token(db, token)
    if user is None:
        raise HTTPException(status_code=400, detail='Invalid token')
    return user


@app.get('/api/topic/{topic_id}', response_model=TopicResponse)
def read_topic(topic_id: int, db: Session = Depends(get_db)):
    response = TopicResponse(data=get_topic(db, topic_id))
    return response


@app.get('/api/thread/{thread_id}', response_model=ThreadResponse)
def read_thread(thread_id: int, db: Session = Depends(get_db)):
    response = ThreadResponse(data=get_thread(db, thread_id))
    return response


@app.get('/api/user', response_model=User)
def read_user(user: User = Depends(require_user)):
    return user


@app.post('/api/authenticate', response_model=TokenResponse)
def request_token(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    if not user_exists(db, form.username):
        raise HTTPException(status_code=401, detail='User does not exist')
    user = get_user_by_name(db, form.username)
    check = check_password(form.password, user.password_hash, user.password_salt)
    if check:
        token = set_user_token(db, form.username)
        return {
            'access_token': token,
            'token_type': 'bearer'
        }
    else:
        raise HTTPException(status_code=401, detail='Wrong password')


@app.post('/api/signup')
def write_user(username: str, password: str, db: Session = Depends(get_db)):
    if user_exists(db, username):
        raise HTTPException(status_code=400, detail='User already exists')
    if not password_is_good(password):
        raise HTTPException(status_code=400, detail='Password is not good')
    add_user(db, username, password)


@app.post('/api/message', status_code=status.HTTP_204_NO_CONTENT)
def post_message(
    thread_id: int,
    message: str,
    user: User = Depends(require_user), db: Session = Depends(get_db)
):
    if thread_exists(db, thread_id):
        add_post(db, thread_id, user, message)
    else:
        raise HTTPException(status_code=400, detail='Thread does not exist')


@app.delete('/api/message', status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    post_id: int,
    user: User = Depends(require_user), db: Session = Depends(get_db)
):
    if post_belongs_to_user(db, post_id, user.id):
        remove_post(db, post_id)
    else:
        raise HTTPException(status_code=400, detail='The post does not belong to the user')
# FIXME: too much data is returned for status code
