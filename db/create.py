from definitions import Base
from fake_data import populate_db

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///db.sqlite')

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

DBsession = sessionmaker(bind=engine)

session = DBsession()
populate_db(session)
