from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine('sqlite:///db.sqlite')
DBSession = sessionmaker(bind=engine)


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
    user_id = Column(Integer, ForeignKey('users.id'))
    text = Column(String)
    parent_id = Column(Integer, ForeignKey('threads.id'))

    parent = relationship('Thread', backref='children_posts')
    user = relationship('User', backref='posts')

    def __repr__(self):
        return f'post [id: {self.id}, user: {self.user}, text: {self.text[:10]}]'


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    password_salt = Column(String, nullable=False)
    token = Column(String, index=True)
    token_expires_at = Column(DateTime)

    def __repr__(self):
        return f'user [id: {self.id}, name: {self.name}]'
