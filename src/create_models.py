"""Create models in object-oriented way using sqlalchemy ORM
"""
from datetime import datetime
from typing import Optional, List
from typing_extensions import Annotated
from sqlalchemy.dialects.postgresql import TIMESTAMP, BIGINT, VARCHAR, INTEGER
from sqlalchemy import DECIMAL
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql.functions import func
from sqlalchemy import ForeignKey, create_engine, URL


# Base classes
class Base(DeclarativeBase):
    """Base class for creating specific objects for database.
    """
    pass


# Mixins
class TimestampMixin:
    """Base class to reuse definitions of columns in other tables.


    Attributes:
    ----------
        created_at (datetime): Date and time of telegram user created by default.
        updated_at (datetime): Date and time of user details updated by default.
    """
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP,
                                                 server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP,
                                                 server_default=func.now(),
                                                 onupdate=func.now())


class TableNameMixin:
    """Mixin class for generating tables names from class names.


    Methods:
    --------
        __tablename__ (class method): Table name to be created from
            inherited class name in database.
    """
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Table name as lower case of class name in plural form.


        Returns:
        -------
            str: Table name as class name for table object in database.
        """
        return cls.__name__.lower() + "s"


# setup mapped_columns overrides providing names for column attributes.

# primary column attribute.
int_pk = Annotated[int, mapped_column(
    INTEGER,
    primary_key=True
)]

# foreign column attribute.
user_fk = Annotated[int, mapped_column(
    BIGINT,
    ForeignKey('users.telegram_id', ondelete='CASCADE')
)]

# string with 255 characters column attribute.
str_255 = Annotated[str, mapped_column(VARCHAR(length=255))]

# column for description.
desc = Annotated[str, mapped_column(VARCHAR(length=3000))]

# column for language code.
lang = Annotated[str, mapped_column(VARCHAR(10))]

# column for cost.
cost = Annotated[float, mapped_column(DECIMAL(precision=16, scale=4))]


# database objects as python classes.

# User.
class User(Base, TimestampMixin, TableNameMixin):
    """class depicting users.


    Attributes:
    -----------
        telegram_id (int): Identifier for telegram user.
        full_name (str): User full name.
        user_name (str or optional): Short name of the user.
        phone_number (str or optional): Phone number of telegram user.
        language_code (str): Language code for user.
        referrer_id (int or optional): refers to telegram user invitee for given telegram user.
    """

    telegram_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)
    full_name: Mapped[str_255]
    user_name: Mapped[Optional[str_255]]
    phone_number: Mapped[Optional[str]] = mapped_column(type_=VARCHAR(length=50))
    language_code: Mapped[lang]
    referrer_id: Mapped[Optional[int]] = mapped_column(
        BIGINT,
        ForeignKey('users.telegram_id', ondelete='SET NULL')
    )

    # reference all orders placed by the user.
    orders: Mapped[List["Order"]] = relationship(back_populates="user")

# Product
class Product(Base, TimestampMixin, TableNameMixin):
    """Class representing product.
    
    Attributes:
    -----------
        product_id (int): Primary key depicting products in database.
        title (str): Product name.
        description (str or optional): Product description.
        price (float): Product price.
    """
    product_id: Mapped[int_pk]
    title: Mapped[str_255] = mapped_column(unique=True)
    description: Mapped[Optional[desc]]
    price: Mapped[cost]

    """ __table_args__ = (
        # unique key constraint on title and description.
        sa.UniqueConstraint('title', 'description',
                             name='products_title_description_key'),
    ) """

# Order.
class Order(Base, TimestampMixin, TableNameMixin):
    """Class representing order.
    
    Attributes:
    -----------
        order_id (int): Primary key depicting orders in database.
        user_id (int): User id referring a telegram user for the given order.
    """
    order_id: Mapped[int_pk]
    user_id: Mapped[user_fk]

    # reference to user that place this order.
    user: Mapped["User"] = relationship("User", back_populates="orders")

    # reference to list of products for this order placed.
    products: Mapped[List["OrderProduct"]] = relationship()

# OrderProduct mapping many-many relationships.
class OrderProduct(Base, TableNameMixin):
    """Class representing many to many relationship.
    
    Many to Many relationship between orders and products
    table in database


    Attributes:
    -----------
        order_id (int): Primary key depicting products in database.
        product_id (int): Primary key depicting products in database.
        quantity (int): Quantity of a given product ordered by user.
    """
    order_id: Mapped[int] = mapped_column(
        INTEGER,
        ForeignKey('orders.order_id', ondelete='CASCADE'),
        primary_key=True
    )
    product_id: Mapped[int] = mapped_column(
        INTEGER,
        ForeignKey('products.product_id', ondelete='RESTRICT'),
        primary_key=True
    )
    quantity: Mapped[int]

    # reference to product placed in order.
    product: Mapped["Product"] = relationship() 


# connect to database engine
url = URL.create(
    # driver name = postgresql + the library we are using (psycopg2)
    drivername="postgresql+psycopg2",
    database='testuser',
    username='testuser',
    password='testpassword',
    host='localhost',
    port=5432
)
engine = create_engine(url=url)

# Bind the engine to session maker.
# session_pool = sessionmaker(bind=engine)

# create all python object to database in unrecommended way.

# drop all tables associated with Base objects from database.
# Base.metadata.drop_all(bind=engine)
# recreate all Base objects as tables in database.
# Base.metadata.create_all(bind=engine)

# connecting to database session.
# with session_pool() as session:
#    pass
