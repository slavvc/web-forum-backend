from db.definitions import Topic, Thread, Post
import schema
from humps import camelize

from sqlalchemy.orm import Session


def get_topic(session: Session, id: int) -> schema.Topic:
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
            link=sub_topic.id
        )
        for sub_topic in topic.children_topics
    )
    threads = (
        schema.ThreadData(
            **camelize(
                schema.DBThread.from_orm(sub_thread).dict()
            ),
            link=sub_thread.id
        )
        for sub_thread in topic.children_threads
    )
    return schema.Topic(
        title=title,
        path=path,
        topics=topics,
        threads=threads
    )


def get_thread(session: Session, id: int) -> schema.Thread:
    thread = session.query(Thread).get(id)
    if thread is None:
        return None
    title = thread.title
    path = get_thread_path(thread)
    posts = (
        schema.PostData(
            **camelize(
                schema.DBPost.from_orm(post).dict()
            )
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
    return [
        {
            'id': topic.id,
            'title': topic.title
        }
        for topic in path
    ]

def get_thread_path(thread):
    parent = thread.parent
    if parent is not None:
        return get_topic_path(parent)
    else:
        return []