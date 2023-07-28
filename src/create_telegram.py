"""Module for creating telegram objects in database.
"""
from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker


# connection string format: dialect+driver://username:password@host:port/database
url = URL.create(
    # dialect name = postgresql + the driver library we are using (psycopg2)
    drivername="postgresql+psycopg2",
    username="testuser",
    password="testpassword",
    database="testuser",
    host="localhost",
    port=5432
)
# create an engine.
# skipped echo=True to avoid printing out all the SQL commands
engine = create_engine(url=url)

# Create a session_pool through engine.
session_pool = sessionmaker(bind=engine)

# Using session_pool connect to database session.
with session_pool() as session:
    query = text("""
        CREATE TABLE users
        (
            telegram_id   BIGINT PRIMARY KEY,
            full_name     VARCHAR(255) NOT NULL,
            user_name      VARCHAR(255),
            language_code VARCHAR(255) NOT NULL,
            created_at    TIMESTAMP DEFAULT NOW(),
            referrer_id   BIGINT,
            FOREIGN KEY (referrer_id)
                REFERENCES users (telegram_id)
                ON DELETE SET NULL
        );
        """)
    # Create user object
    # session.execute(statement=query)

    insert_query = text("""
            INSERT INTO users (telegram_id, full_name, user_name, language_code, referrer_id)
            VALUES (1, 'John Doe', 'johndoe', 'en', NULL), (2, 'Jane Doe', 'janedoe', 'en', 1);
        """)
    # Add users to user table.
    #session.execute(statement=insert_query)

    # fetch rows from users table created in database.
    select_query = text("""
            SELECT * FROM users;
        """)
    result = session.execute(statement=select_query)
    for row in result:
        print(row)

    # execute result
    result = session.execute(statement=select_query)
    print(f"execute result: {result}")

    # all result
    result = session.execute(statement=select_query).all()
    print(f"all result as list of RowProxy objects:{result}")

    # fetchall result
    result = session.execute(statement=select_query).fetchall()
    print(f"fetchall result: {result}")

    # fetchone result
    result = session.execute(statement=select_query).fetchone()
    print(f"fetchone result (one row): {result}")

    # first result
    result = session.execute(statement=select_query).first()
    print(f"first result (one row): {result}")

    # scalar result
    filter_query = text("SELECT user_name FROM users WHERE telegram_id = :telegram_id")
    result = session.execute(statement=filter_query, params={"telegram_id": 1}).scalar()
    print(f"scalar result username: {result}")

    # scalars result
    scalars_query = text("SELECT user_name FROM users")
    result = session.execute(statement=scalars_query).scalars()
    print(f"scalars result username column: {result}")

    # scalars with fetch all values in column username
    result = session.execute(statement=scalars_query).scalars().fetchall()
    print(f"scalars result fetch username (all rows in column): {result}")

    # scalar one or none result
    result = session.execute(statement=filter_query,
                             params={"telegram_id": 12345}).scalar_one_or_none()
    print(f"scalar one or none result username: {result}")

    # full name of filtered query
    fullname = session.execute(statement=text(
                                """SELECT
                                full_name FROM users
                                WHERE telegram_id = :telegram_id"""
                                ).params(telegram_id = 1)
                        ).fetchone()
    print(f"full name result (one row): {fullname}")

    # Commit all the changes to database.
    #session.commit()

# closes the session after exiting the context manager.
