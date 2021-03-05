from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship


Base = declarative_base()

class Topic(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    num_topics = Column(Integer)
    num_threads = Column(Integer)
    last_post = Column(String)

    parent_id = Column(Integer, ForeignKey('topics.id'))
    parent = relationship('Topic', remote_side=[id], backref='children_topics')

    def __repr__(self):
        return f'topic [id: {self.id}, title: {self.title}]'

class Thread(Base):
    __tablename__ = 'threads'

    id = Column(Integer, primary_key=True)
    
    title = Column(String)
    num_posts = Column(Integer)
    last_post = Column(String)
    is_vegan = Column(Boolean)

    parent_id = Column(Integer, ForeignKey('topics.id'))
    parent = relationship('Topic', backref='children_threads')
    
    def __repr__(self):
        return f'thread [id: {self.id}, title: {self.title}]'

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    user = Column(String)
    text = Column(String)

    parent_id = Column(Integer, ForeignKey('threads.id'))
    parent = relationship('Thread', backref='children_posts')
    
    def __repr__(self):
        return f'post [id: {self.id}, user: {self.user}, text: {self.text[:10]}]'