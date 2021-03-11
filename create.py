from db_definitions import Base, DBSession
from fake_data import populate_db

session = DBSession()
try:
    engine = session.get_bind()

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    populate_db(session)
finally:
    session.close()
