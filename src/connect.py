"""Module for connecting to database.
"""
from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker


# connection string format: dialect+driver://username:password@host:port/database
url = URL.create(
    # driver name = postgresql + the library we are using (psycopg2)
    drivername="postgresql+psycopg2",
    username='testuser',
    password='testpassword',
    host="localhost",
    database='testuser',
    port=5432
)
engine = create_engine(
    url=url,
    echo=True)

# a sessionmaker(), also in the same scope as the engine
session_pool = sessionmaker(bind=engine)
# we can now construct a session_pool() without needing to pass the
# engine each time
with session_pool() as session:
    # session.add(some_other_object)
    session.execute(statement=text("SELECT 1=1"))
    session.commit()
# closes the session after exiting the context manager.
