from .definitions import Topic, Thread, Post

# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine

# engine = create_engine('sqlite:///db.sqlite')

# DBsession = sessionmaker(bind=engine)
# session = DBsession()

def get_topic(session, id):
    return session.query(Topic).get(id)

def get_thread(session, id):
    return session.query(Thread).get(id)

def get_thread_posts(session, id):
    thread = get_thread(session, id)
    return thread.children_posts if thread is not None else None

def get_topic_path(topic):
    path = [topic]
    def recur_add_parent(topic):
        nonlocal path
        parent = topic.parent
        if parent is not None:
            path.append(parent)
            recur_add_parent(parent)
    return path