from lorem import get_paragraph, get_sentence, get_word
from definitions import Topic, Thread, Post
from random import randint

def make_topic():
    return Topic(
        title=get_word()
    )

def make_thread():
    return Thread(
        title=get_word(),
        is_vegan=randint(0,1) == 1
    )

def make_post():
    return Post(
        user='$username',
        text=get_sentence()
    )

def make_topic_tree(depth):
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
                for _ in range(num_posts):
                    post = make_post()
                    post.parent = thread
                    posts.append(post)

    topics = []
    threads = []
    posts = []
    recur(0, None)

    return {
        'topics': topics, 
        'threads': threads, 
        'posts': posts
    }
    

def populate_db(session):
    data = make_topic_tree(5)

    for item in data['topics'] + data['threads'] + data['posts']:
        session.add(item)
    session.commit()