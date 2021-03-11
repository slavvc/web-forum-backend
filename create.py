from db_definitions import Base
from fake_data import populate_db

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///db.sqlite')

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)

session = DBSession()
populate_db(session)
