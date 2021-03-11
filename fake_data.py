from lorem import get_sentence, get_word
from db_definitions import Topic, Thread, Post, User
from random import randint
from utils import make_password


def make_topic():
    return Topic(
        title=get_word()
    )


def make_thread():
    return Thread(
        title=get_word(),
        is_vegan=randint(0,1) == 1
    )


def make_post(user_id):
    return Post(
        user_id=user_id,
        text=get_sentence()
    )


USER_NUMBER = 1


def make_user():
    global USER_NUMBER
    hash, salt = make_password(f'Password{USER_NUMBER}')
    user = User(
        name=f'User{USER_NUMBER}',
        password_hash=hash,
        password_salt=salt
    )
    USER_NUMBER += 1
    return user


def make_topic_tree(depth, n_users):
    def recur(current_depth, parent):
        nonlocal topics, threads, posts
        if current_depth < depth:
            num_topics = randint(1, 10)
            num_threads = randint(0, 10)
            if parent is not None:
                parent.num_topics = num_topics
                parent.num_threads = num_threads
            
            for _ in range(num_topics):
                topic = make_topic()
                topic.parent = parent
                topics.append(topic)
                recur(current_depth+1, topic)

            for _ in range(num_threads):
                thread = make_thread()
                thread.parent = parent
                threads.append(thread)

                num_posts = randint(0, 10)
                thread.num_posts = num_posts
                for _ in range(num_posts):
                    user_id = randint(0, n_users)
                    post = make_post(user_id)
                    post.parent = thread
                    posts.append(post)

    topics = []
    threads = []
    posts = []
    users = [
        make_user()
        for _ in range(n_users)
    ]
    recur(0, None)

    return {
        'topics': topics, 
        'threads': threads, 
        'posts': posts,
        'users': users
    }
    

def populate_db(session):
    data = make_topic_tree(5, 10)
    data['topics'][0].id = 0
    data['threads'][0].id = 0
    data['posts'][0].id = 0
    data['users'][0].id = 0
    for item in (
              data['topics']
            + data['threads']
            + data['posts']
            + data['users']
    ):
        session.add(item)
    session.commit()
