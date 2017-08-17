from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils.functions import database_exists, create_database

from .models import Base, JamTimeseries

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.

database_path = "sqlite:///data.db"
created = False
if not database_exists(database_path):
    created = True
    create_database(database_path)

engine = create_engine(database_path, convert_unicode=True)
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))
Base.query = session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)


if created:
    print("Just created new db")
    init_db()
