from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils.functions import database_exists, create_database

from .models import Base, JamTimeseries

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.

# database_path = "sqlite:///data.db"
# created = False
# if not database_exists(database_path):
#     created = True
#     create_database(database_path)

# engine = create_engine(database_path, convert_unicode=True)
# session = scoped_session(sessionmaker(autocommit=False,
#                                       autoflush=False,
#                                       bind=engine))
# Base.query = session.query_property()

engine = None
created = False
session = None


def get_session(db_path):
    global created, engine, session
    if not db_path.startswith("sqlite3:"):
        db_path = "sqlite:///" + db_path

    print("db.get_session db_path: %s" % db_path)
    if not created:
        if not database_exists(db_path):
            created = True
            create_database(db_path)

        engine = create_engine(db_path, convert_unicode=True)
        if created:
            init_db()
        session = scoped_session(sessionmaker(autocommit=True,
                                              autoflush=False,
                                              bind=engine))

    return session


def init_db():
    Base.metadata.create_all(bind=engine)


if created:
    print("Just created new db")
    init_db()
