from typing import Optional, Union
from db_definitions import Topic, Thread, Post, User, Base, DBSession
import schema
from humps import camelize
from datetime import datetime, timedelta
import os

from utils import make_password, make_token

from sqlalchemy.orm import Session

ROOT_PASSWORD = os.environ['ROOT_PASSWORD'] if 'ROOT_PASSWORD' in os.environ else 'toor'


def init_db():
    session = DBSession()
    engine = session.get_bind()
    Base.metadata.create_all(engine)
    root_exists = session.query(User).filter(User.id == 0).count()
    if not root_exists:
        hash, salt = make_password(ROOT_PASSWORD)
        root_user = User(
            id=0,
            name='root',
            password_hash=hash,
            password_salt=salt
        )
        session.add(root_user)
    home_exists = session.query(Topic).filter(Topic.id == 0).count()
    if not home_exists:
        home_topic = Topic(
            id=0,
            title='Home',
            user_id=0
        )
        session.add(home_topic)
    session.commit()


def get_topic(session: Session, id: int) -> Optional[schema.Topic]:
    topic = session.query(Topic).get(id)
    if topic is None:
        return None
    path = get_topic_path(topic)
    title = topic.title
    topics = (
        schema.TopicData(
            **camelize(
                schema.DBTopic.from_orm(sub_topic).dict()
            ),
            link=sub_topic.id,
            numTopics=len(sub_topic.children_topics),
            numThreads=len(sub_topic.children_threads),
            user=schema.User.from_orm(sub_topic.user)
        )
        for sub_topic in topic.children_topics
    )
    threads = (
        schema.ThreadData(
            **camelize(
                schema.DBThread.from_orm(sub_thread).dict()
            ),
            link=sub_thread.id,
            numPosts=len(sub_thread.children_posts),
            user=schema.User.from_orm(sub_thread.user)
        )
        for sub_thread in topic.children_threads
    )
    return schema.Topic(
        title=title,
        path=path,
        topics=topics,
        threads=threads,
        user=schema.User.from_orm(topic.user)
    )


def get_thread(session: Session, id: int) -> Optional[schema.Thread]:
    thread = session.query(Thread).get(id)
    if thread is None:
        return None
    title = thread.title
    path = get_thread_path(thread)
    posts = (
        schema.PostData(
            **camelize(
                schema.DBPost.from_orm(post).dict()
            ),
            user=schema.User.from_orm(post.user)
        )
        for post in thread.children_posts
    )
    return schema.Thread(
        title=title,
        path=path,
        posts=posts
    )


def get_thread_posts(session, id):
    thread = get_thread(session, id)
    return thread.children_posts if thread is not None else None


def get_topic_path(topic: Topic) -> schema.Path:
    path = [topic]

    def recur_add_parent(topic):
        nonlocal path
        parent = topic.parent
        if parent is not None:
            path.append(parent)
            recur_add_parent(parent)
    recur_add_parent(topic)
    return [
        schema.PathElement(
            id=topic.id,
            title=topic.title
        )
        for topic in reversed(path)
    ]


def get_thread_path(thread):
    parent = thread.parent
    if parent is not None:
        return get_topic_path(parent)
    else:
        return []


# def get_user_by_id(session: Session, id: int) -> Optional[schema.User]:
#     user = session.query(User).get(id)
#     if user is None:
#         return None
#     db_user = schema.DBUser.from_orm(user)
#     return schema.User(**db_user.dict())


def get_user_by_name(session: Session, username: str) -> schema.DBUser:
    user = session.query(User).filter(User.name == username).one()
    db_user = schema.DBUser.from_orm(user)
    return db_user


def get_user_by_token(session: Session, token: str) -> Optional[schema.User]:
    users = session.query(User).filter(User.token == token).all()
    if len(users) != 1:
        return None
    user = users[0]
    db_user = schema.DBUser.from_orm(user)
    if datetime.now() > db_user.token_expires_at:
        return None
    return schema.User(**db_user.dict())


def set_user_token(session: Session, username: str) -> str:
    token = make_token()
    expires_at = datetime.now() + timedelta(days=1)
    session.query(User).filter(User.name == username)\
        .update({
            User.token: token,
            User.token_expires_at: expires_at
        })
    session.commit()
    return token


def add_user(session: Session, username: str, password: str):
    hash, salt = make_password(password)
    user = User(
        name=username,
        password_hash=hash,
        password_salt=salt
    )
    session.add(user)
    session.commit()


def user_exists(session: Session, username: str):
    count = session.query(User).filter(User.name == username).count()
    return count == 1


def thread_exists(session: Session, thread_id: int):
    count = session.query(Thread).filter(Thread.id == thread_id).count()
    return count == 1


def add_post(session: Session, thread_id: int, user: schema.User, text: str):
    post = Post(
        user_id=user.id,
        text=text,
        parent_id=thread_id
    )
    session.add(post)
    session.commit()


DB_SCHEMA = {
    Post: schema.DBPost,
    Thread: schema.DBThread,
    Topic: schema.DBTopic
}


def row_belongs_to_user(
        session: Session, row_id: int,
        user_id: int, table: Union[Post, Thread, Topic]
):
    row: Optional[table] = session.query(table).get(row_id)
    if row is None:
        return False
    db_row = DB_SCHEMA[table].from_orm(row)
    return db_row.user_id == user_id


def remove_row(session: Session, row_id: int, table: Union[Post, Thread, Topic]):
    row = session.query(table).get(row_id)
    session.delete(row)
    session.commit()


def post_belongs_to_user(session: Session, post_id: int, user_id: int) -> bool:
    return row_belongs_to_user(session, post_id, user_id, Post)


def remove_post(session: Session, post_id: int):
    post = session.query(Post).get(post_id)
    session.delete(post)
    session.commit()


def topic_exists(session: Session, topic_id: int) -> bool:
    count = session.query(Topic).filter(Topic.id == topic_id).count()
    return count == 1


def add_topic(session: Session, title: str, parent_id: int, user_id: int):
    topic = Topic(
        title=title,
        parent_id=parent_id,
        user_id=user_id
    )
    session.add(topic)
    session.commit()


def add_thread(session: Session, title: str, is_vegan: bool, parent_id: int, user_id: int):
    thread = Thread(
        title=title,
        is_vegan=is_vegan,
        parent_id=parent_id,
        user_id=user_id
    )
    session.add(thread)
    session.commit()


def remove_topic(session: Session, topic_id: int):
    remove_row(session, topic_id, Topic)


def remove_thread(session: Session, thread_id: int):
    remove_row(session, thread_id, Thread)


def thread_belongs_to_user(session: Session, thread_id: int, user_id: int):
    return row_belongs_to_user(session, thread_id, user_id, Thread)


def topic_belongs_to_user(session: Session, topic_id: int, user_id: int):
    return row_belongs_to_user(session, topic_id, user_id, Topic)
