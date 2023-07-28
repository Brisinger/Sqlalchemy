"""Module to store and manage database interactions.

Sending and receiving queries and results to and from sqlalchemy.orm
respectively by connecting to PostgreSQL Database session.
"""
from sqlalchemy import insert, select, func
from sqlalchemy import create_engine, URL, or_
from sqlalchemy.orm import Session, sessionmaker, aliased
from sqlalchemy.dialects.postgresql import (
    insert as insert_combined
)
from create_models import User, Order, Product, OrderProduct
from environs import Env
from typing import Any, List
from faker import Faker
import random


# implement the Repo class.
class Repo:
    """Class to manage and store database interactions.
    
    
    Methods:
    -------
        add_user( 
            telegram_id: int,
            full_name: str,
            language_code: str,
            username: str = None,
            phone_number: str = None,
            referrer_id: int = None,
        ): Persists an user instance to database.
        get_user_by_id(telegram_id: int): Returns the user for given
            telegram_id fetched from database.
        get_all_users(): Returns all users fetched from database.
        get_user_language_code(telegram_id: int): Returns the language_code 
            from user with given telegram_id fetched from database.
        get_all_users_advanced(): Returns top 10 list of users ordered in descending by created_at date
            with language_code english or ukranian and filtered for positive telegram_id.
        add_user_combined(
            telegram_id: int,
            full_name: str,
            language_code: str,
            username: str = None,
            phone_number: str = None,
            referrer_id: int = None,
        ): Persists an user instance to database and returns it.
        add_order(user_id: int): Returns the order placed by a
            telegram user after adding it to database.
        add_product(title: str, description: str, price: float): Returns the product 
            bought by a telegram user after adding it to database.
        add_order_product(
            order_id: int,
            product_id: int,
            quantity: int): Returns the orderproduct mapping 
            after storing and comitting it to database.
        seed_fake_data(): Populates users, products, orders and orderproduct mapping tables.
        select_all_invited_users(): Returns List of user fullname and their referral full names.
        get_all_user_orders_user_full(telegram_id: int): Returns List of orders for telegram user.
        get_all_user_orders_user_only_user_name(telegram_id: int): Returns List of orders with 
            user_name for a give telegram user.
        get_all_user_orders_relationships(telegram_id: int): Returns List of products, orders
            with user_name and quantity for a given telegram user.
        get_all_user_orders_no_relationships(telegram_id: int): Returns List of products, orders
            with user_name and quantity for a given telegram user.
        get_user_total_number_of_orders(telegram_id: int): Returns No. of orders from telegram user
            as a scalar integer.
        get_total_number_of_orders_by_user(): Returns total orders and id of telegram user across users.
        get_total_number_of_orders_by_user_with_labels(): Returns Sequence of rows of tuples
            containing  quantity of orders and name.
        get_count_of_products_by_user(): Returns Sequence of rows of tuples containing total 
            quantity of products labeled as quantity along with user's full name labeled as name from database based on the orders placed by telegram user.
        get_count_of_products_greater_than_x_by_user(greater_than: int): Returns Sequence of rows
            of tuples containing total quantity of products labeled as quantity along with user's
            full name labeled as name from database based on the orders placed by telegram users
            with quantity of product ordered greater than specified amount.
    """
    def __init__(self, session:Session) -> None:
        """initializes databases session
        
        
        Args:
        -----
            session (Session): Database sesion pool connection using orm session.
        """
        self._session:Session = session

    def add_user(
        self,
        telegram_id: int,
        full_name: str,
        language_code: str,
        username: str = None,
        phone_number: str = None,
        referrer_id: int = None,
    ) -> None:
        """Creates an user instance for user object.
        
        Persists user instance into PostgreSql database.

        Args:
        -----
            telegram_id (int): Identifier for telegram user.
            full_name (str): User full name.
            language_code (str): Language code for user.
            username (str or optional): Short name of the user.
            phone_number (str or optional): Phone number of telegram user.
            referrer_id (int or optional): refers to telegram user invitee for given telegram user.
        """
        # insert query.
        stmt = insert(User).values(
            telegram_id=telegram_id,
            full_name=full_name,
            user_name=username,
            phone_number=phone_number,
            language_code=language_code,
            referrer_id=referrer_id,
        )

        # execute insert query on orm session.
        self._session.execute(statement=stmt)

        # commit changes into database.
        self._session.commit()

    def add_user_combined(
            self,
            telegram_id: int,
            full_name: str,
            language_code: str,
            username: str = None,
            phone_number: str = None,
            referrer_id: int = None,
        )-> User:
        """Fetches user instance added or updated in database.
        
        The user object is fetched if it does not exist in
        database it is inserted into table as a new object.
        User object is fetched after inserting in database.
        If user already in database then update user object.
        Update user instance and then fetch the updated user.

        Notice the import statement at the beginning of this
        cell. `.returning(...)` and `.on_conflict_do_nothing()` (as well as
        `.on_conflict_do_update(...)`) methods aren't accessible by using basic
        `sqlalchemy.insert` constructor. These are parts of PostgreSQL dialect.
        What are we trying to achieve? We want to INSERT user every time and
        SELECT it if no conflict occurs (on the DB side). And, if there is a
        conflict, do UPDATE and only then SELECT updated row.


        Args:
        -----
            telegram_id (int): Identifier for telegram user.
            full_name (str): User full name.
            language_code (str): Language code for user.
            username (str or optional): Short name of the user.
            phone_number (str or optional): Phone number of telegram user.
            referrer_id (int or optional): refers to telegram user invitee for given telegram user.

        Returns:
        --------
            User instance after being inserted or updated in database. 
        """
        # insert statement query.
        insert_stmt = insert_combined(
                        User
                    ).values(
                        telegram_id=telegram_id,
                        full_name=full_name,
                        language_code=language_code,
                        user_name=username,
                        phone_number=phone_number,
                        referrer_id=referrer_id,
                        # Also, another method which uses raw PostgreSQL instruction,
                        # such as ON CONFLICT DO ...
                        # In that case, we are using ON CONFLICT DO UPDATE, but 
                        # ON CONFLICT DO NOTHING is also achievable by using 
                        # `.on_conflict_do_nothing()` method.
                    ).on_conflict_do_update(    
                        # `index_elements` argument is for array of entities used
                        # in order to distinguish records from each other.
                        index_elements=[User.telegram_id],
                        # `set_` argument (we add underscore at the end because 
                        # `set` is reserved name in python, we can't use it as 
                        # a key) used to define which columns you wish to update
                        # in case of conflict. Almost identical to use of `.values()` method.
                        set_=dict(
                            user_name=username,
                            full_name=full_name,
                        ),
                        # Here we are using new method which represents RETURNING 
                        # instruction in raw SQL (particularly PostgreSQL syntax)
                    ).returning(User,)
        
        # And here we are declaring that we want to SELECT .
        # the entity from our INSERT statement.
        stmt = select(User).from_statement(insert_stmt)

        # Also, here is another way to execute your statement and retrieve data.
        # You can use `session.scalars(stmt)` instead of `session.execute(stmt).scalars()`.
        result = self._session.scalars(statement=stmt)

        # commit changes to database.
        self._session.commit()

        # fetch user instance committed to database.
        return result.first()

    def get_user_by_id(self, telegram_id: int)-> User:
        """Fetch an user in telegram from database.
        
        The user instance associated with given telegram_id
        is queried to and returned from database.

        Notice that you should pass the comparison-like arguments 
        to WHERE statement, as you can see below, we are using 
        `User.telegram_id == telegram_id` instead of 
        `User.telegram_id = telegram_id`
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = self.session.execute(stmt)
        After we get the result of our statement execution, we need to
        define HOW we want to get the data. In most cases you want to 
        get the object(s) or only one value. To retrieve the object 
        itself, we call the `scalars` method of our result. Then we 
        have to define HOW MANY records you want to get. It can be 
        `first` object, `one` (raises an error if there are not 
        exactly one row retrieved)) / `one_or_none` and so on.
        

        Args:
        -----
            telegram_id (int): Identifier for telegram user.

        Returns:
        --------
            User: An user associated with given telegram_id.
        """
        # select query.
        stmt = select(User).where(User.telegram_id==telegram_id)

        # execute select query on orm session.
        result = self._session.execute(statement=stmt)

        # retrieve the user object and return the first entry.
        return result.scalars().first()

    def get_all_users(self)-> List[User]:
        """Fetch all telegram users.
        
        Returns list of telegram users from database.


        Returns:
        --------
            List of all users fetched from database.
        """
        # select query.
        stmt = select(User)

        # execute select query on orm session.
        result = self._session.execute(statement=stmt)

        # return all users fetched from database.
        return result.scalars().fetchall()

    def get_user_language_code(self, telegram_id: int)-> str:
        """Get user's language code from database for given telegram_id.
        

        Args:
        -----
            telegram_id: Identifier for telegram user.

        Returns:
        --------
            language code of retrieved user for given telegram_id.
        """
        # select query.
        stmt = select(User.language_code).where(User.telegram_id==telegram_id)

        # execute select query on orm session.
        result = self._session.execute(statement=stmt)

        # return the language code retrieved from given user.
        return result.scalar()

    def get_all_users_advanced(self) -> List[User]:
        """ Fetches first 10 users ordered by created_at date in descending 
        order with user name starting with john and with language_code english or ukranian.

        The users are grouped by telegram_id and filtered with positive id's.


        Returns:
        --------
            List of users satisfying the given condition.
        """
        # select users query.
        stmt = select(
            User,
        ).where(
            # OR clauses' syntax is explicit-only, unlike the AND clause.
            # You can pass each argument of OR statement as arguments to 
            # `sqlalchemy.or_` function, like on the example below
            or_(
                User.language_code == 'en',
                User.language_code == 'uk',
            ),
            # Each argument that you pass to `where` method of the Select object 
            # considered as an argument of AND statement
            User.user_name.ilike('%john%'),
        ).order_by(
            User.created_at.desc(),
        ).limit(
            10,
        ).having(
            User.telegram_id > 0,
        ).group_by(
            User.telegram_id,
        )
    
        # fetch users based on select query execution from database.
        result = self._session.execute(stmt)

        # return list of users.
        return result.scalars().all()

    def add_order(self, user_id: int)-> Order:
        """Adds order for given user.
        The order from user is created and added to database.


        Args:
        ----
            user_id (int): User id referring a telegram user for the given order.

        Returns:
        --------
            The order placed by user after commiting it to database.
        """
        # insert order query.
        # An user can place multiple orders. Same user is inserted for different orders.
        # There is no need to use `on_conflict_*` method as there is no conflict for user.
        insert_stmt = insert_combined(Order).values(
                        user_id=user_id
                    ).returning(Order,)
        
        # select order query.
        # fetch the order place by user after storing in database.
        stmt = select(Order).from_statement(insert_stmt)

        # Also, here is another way to execute your statement and retrieve data.
        # You can use `session.scalars(stmt)` instead of `session.execute(stmt).scalars()`.
        result = self._session.scalars(statement=stmt)

        # commit changes to database.
        self._session.commit()

        # fetch order instance committed to database.
        return result.first()        

    def add_product(self, title: str, description: str, price: float)-> Product:
        """Adds the product to database for the order placed by telegram user.
        
        Product is returned after product ordered is comitted to database.


        Args:
        -----
            title (str): Product name.
            description (str or optional): Product description.
            price (float): Product price.

        Returns:
        --------
            Product added to database.
        """
        # insert product query.
        # There can be only one product with give title, description and price.
        # There is a need to use `on_conflict_*` method as there can be conflict.
        insert_stmt = insert_combined(Product).values(
                                                    title=title,
                                                    description=description,
                                                    price=price
                                                ).on_conflict_do_update(
                                                    index_elements=[Product.title],
                                                    set_=dict(
                                                        price=price,
                                                    ),
                                                ).returning(Product)

        # select product query.
        # fetch the product bought by user after storing in database.
        stmt = select(Product).from_statement(insert_stmt)

        # Also, here is another way to execute your statement and retrieve data.
        # You can use `session.scalars(stmt)` instead of `session.execute(stmt).scalars()`.
        result = self._session.scalars(statement=stmt)

        # commit changes to database.
        self._session.commit()

        # fetch product instance committed to database.
        return result.first()        

    def add_order_product(self, order_id: int, product_id: int, quantity: int)-> OrderProduct:
        """Adds Order and associated Product identifiers into database.
        
        Each product can be associated with multiple orders and
        each order can be associated with multiple products.
        This many-many mapping between order and product is stored in database.
        The order-product mapping added is returned after comitting to database.


        Args:
        -----
            order_id (int): Primary key depicting products in database.
            product_id (int): Primary key depicting products in database.
            quantity (int): Quantity of a given product ordered by user. 

        Returns:
        --------
            OrderProduct mapping after comitting it to database.
        """
        # insert order-product mapping query.
        # There can be only one order mapped to give product.
        # There is a need to use `on_conflict_*` method as there can be conflict.
        insert_stmt = insert_combined(
                        OrderProduct).values(
                                        order_id=order_id,
                                        product_id=product_id,
                                        quantity=quantity
                                    ).on_conflict_do_update(
                                        index_elements=[OrderProduct.order_id,
                                                        OrderProduct.product_id,
                                                        ],
                                        set_=dict(
                                            quantity=quantity,
                                        ),
                                    ).returning(OrderProduct)

        # select order-product mapping query.
        # fetch the order-product mapping after storing in database.
        stmt = select(OrderProduct).from_statement(insert_stmt)

        # Also, here is another way to execute your statement and retrieve data.
        # You can use `session.scalars(stmt)` instead of `session.execute(stmt).scalars()`.
        result = self._session.scalars(statement=stmt)

        # commit changes to database.
        self._session.commit()

        # fetch order-product instance committed to database.
        return result.first()        

    def seed_fake_data(self):
        """Populate initial data.
        
        Populates users, product, orders and orderproduct mapping tables.
        """
        # Here we can define something like randomizing key.
        # If we pass same seed every time we would get same 
        # sequence of random data.
        Faker.seed(0)
        fake = Faker()
        # Lets predefine our arrays of fake entities so we 
        # can reference them to create relationships and(or)
        # to give referrer_id to some users and so on.
        users = self.get_all_users()
        orders = []
        products = []

        # add users
        for _ in range(10):
            referrer_id = None if not users else users[-1].telegram_id
            user = self.add_user_combined(
                            telegram_id=fake.pyint(),
                            full_name=fake.name(),
                            language_code=fake.language_code(),
                            username=fake.user_name(),
                            phone_number=fake.phone_number(),
                            referrer_id=referrer_id,
                        )
            users.append(user)

        # add orders
        for _ in range(10):
            order = self.add_order(
                            user_id=random.choice(users).telegram_id,
                        )
            orders.append(order)

        # add products
        for _ in range(10):
            product = self.add_product(
                            title=fake.word(),
                            description=fake.sentence(),
                            price=fake.pyfloat(left_digits=11,
                                              right_digits=4,
                                              positive=True),
                            )
            products.append(product)

        # add products to orders
        for order in orders:
            # Here we use `sample` function to get list of 3 unique products
            for product in random.sample(products, 3):
                self.add_order_product(
                        order_id=order.order_id,
                        product_id=product.product_id,
                        quantity=fake.pyint(),
                    )

    def select_all_invited_users(self):
        """Selects list of user and their referrals.


        Returns:
        --------
            List of user fullname and their referral full names.
        """
        ParentUser = aliased(User)
        ReferralUser =  aliased(User)

        # self referential join query.
        stmt = (
            select(
                ParentUser.full_name.label("parent_name"),
                ReferralUser.full_name.label("referral_name")
            ).join(
                target=ReferralUser, 
                onclause=(ReferralUser.referrer_id == ParentUser.telegram_id)
            )
        )
        
        # execute the join query
        result = self._session.execute(statement=stmt)

        # return list of user objects.
        return result.fetchall()

    def get_all_user_orders_user_full(self, telegram_id: int):
        """Fetches orders of each user given their telegram_id.
        

        Args:
        -----
            telegram_id (int): Identifier for telegram user.
        
        Returns:
        -------
            List of orders for a give telegram user.
        """
        # select orders of user in join query.
        stmt = (
            select(Order, User).join(User.orders).where(User.telegram_id == telegram_id)
        )
        
        # NOTICE: Since we are joining two tables, we won't use `.scalars()` method.
        # Usually we want to use scalars if we are joining multiple tables or 
        # when you use `.label()` method to retrieve some specific column etc.
        result = self._session.execute(stmt)

        # fetch the result.
        return result.all()

    def get_all_user_orders_user_only_user_name(self, telegram_id: int):
        """Fetches orders of each user given their telegram_id.
        
        The orders for each user is joined with user_name column.


        Args:
        -----
            telegram_id (int): Identifier for telegram user.
        
        Returns:
        -------
            List of orders with user_name for a give telegram user.
        """
        # select orders of user in join query.
        stmt = (
            select(Order, User.user_name).join(User.orders).where(User.telegram_id == telegram_id)
        )

        # execute the join query with right hand user table column user_name.
        result = self._session.execute(stmt)

        # fetch the result of join query.
        return result.all()

    def get_all_user_orders_relationships(self, telegram_id: int):
        """Fetches all products and quantity ordered by user with given telegram_id.
        
        The orders for each user is joined with user_name column.
        Product details along with quantity purchased for given order
        is fetched through join statement on multiple object tables.


        Args:
        -----
            telegram_id (int): Identifier for telegram user.
        
        Returns:
        -------
            List of products, orders with user_name
            and quantity for a given telegram user.
        """
        # join query with Product, Order and User object tables.
        stmt = (
            select(
                Product,
                Order,
                User.user_name,
                OrderProduct.quantity,
            ).join(
                target=User.orders
            ).join(
                target=Order.products
            ).join(
                target=Product
            ).where(User.telegram_id == telegram_id)
        )

        # execute the join query.
        result = self._session.execute(statement=stmt)

        # fetch all the Products, for every Order by user name 
        # and quantity of product purchased by given telegram user.
        return result.fetchall()

    def get_all_user_orders_no_relationships(self, telegram_id: int):
        """Fetches all products and quantity ordered by user with given telegram_id.
        
        The orders for each user is joined with user_name column.
        Product details along with quantity purchased for given order
        is fetched through join statement on multiple object tables.

        The product, orders and user names along with quantity of 
        product ordered is correlated with unrelatable join relations.


        Args:
        -----
            telegram_id (int): Identifier for telegram user.

        Returns:
        -------
            List of products, orders with user_name
            and quantity for a given telegram user.
        """
        # join query with Product, Order and User object tables without relationships.
        stmt = (
            select(Product, Order, User.user_name, OrderProduct.quantity)
            .join(OrderProduct)
            .join(Order)
            .join(User)
            .select_from(Product)
            .where(User.telegram_id == telegram_id)
        )

        # execute the join query.
        result = self._session.execute(statement=stmt)

        # fetch all the Products, for every Order by user name 
        # and quantity of product purchased by given telegram user.
        return result.fetchall()

    def get_user_total_number_of_orders(self, telegram_id: int):
        """Total number of orders placed by given telegram user.
        
        
        Args:
        -----
            telegram_id (int): Identifier for telegram user.

        Returns:
        --------
            No. of orders from telegram user as a scalar integer.
        """
        # aggregation query.
        stmt = (
            # All SQL aggregation functions are accessible with `sqlalchemy.func` module
            select(func.count(Order.order_id)).where(Order.user_id == telegram_id)
        )

        # As you can see, if we want to get only one value with our query,
        # we can just use `.scalar(stmt)` method of our Session.
        # execute the aggregation query to get a scalar result .
        result = self._session.scalar(statement=stmt)

        # return the aggregatio result.
        return result

    def get_total_number_of_orders_by_user(self):
        """Total number of orders with user id returned.
        

        Returns:
        --------
            No. of orders and id of telegram user across users.
        """
        # aggregation query.
        stmt = (
            select(func.count(Order.order_id), User.telegram_id)
            .join(User)
            .group_by(User.telegram_id)
        )

        # As you can see, if we want to get a recirde with our query,
        # we cannot use `.scalar(stmt)` method of our Session.
        # execute the aggregation query and return ResultProxy object.
        result = self._session.execute(statement=stmt)

        # return the row of tuples.
        return result.all()

    def get_total_number_of_orders_by_user_with_labels(self):
        """Total orders, user full name with labels.
        
        Fetches total orders placed by telegram users
        along with user's full name from database.

        The aggregate result computed is labeled quatity.
        The full name of telegram user is labelled name.


        Returns:
        --------
            Sequence of rows of tuples containing quantity of orders and name. 
        """
        # Aggregate join query with labels.
        stmt = (
            select(func.count(Order.order_id).label('quantity'), User.full_name.label('name'))
            .join(User)
            .group_by(User.telegram_id)
        )

        # execute join query.
        result = self._session.execute(stmt)

        # returns sequence of fetched rows with aggregate result.
        return result.all()

    def get_count_of_products_by_user(self):
        """Total no. of products ordered by telegram user.
        
        Fetches rows containing sum of all products labeled quantity
        ordered by telegram user with full name labeled name and 
        grouped by user's telegram id.


        Returns:
        --------
            Sequence of rows of tuples containing total quantity of products
            labeled as quantity along with user's full name labeled as name
            from database based on the orders placed by telegram user.
        """
        # aggregate join query grouped by telegram user id.
        stmt = (
            select(func.sum(OrderProduct.quantity).label('quantity'), User.full_name.label('name'))
            .join(Order, Order.order_id == OrderProduct.order_id)
            .join(User)
            .group_by(User.telegram_id)
        )

        # execute the join query.
        result = self._session.execute(stmt)
        
        # return sequence of fetched rows with aggregate result.
        return result.all()

    def get_count_of_products_greater_than_x_by_user(self, greater_than: int):
        """Total no. of products ordered by telegram users greater than a given amount.
        
        Fetches rows containing sum of all products labeled quantity ordered by 
        telegram users with full name labeled name grouped by user's telegram id.
        The grouped aggregate result is filtered with users that ordered more than
        specified amount of products.


        Args:
        -----
            greater_than (int): Quantity of given product ordered by telegram user.

        Returns:
        --------
            Sequence of rows of tuples containing total quantity of products labeled as quantity
            along with user's full name labeled as name from database based on the orders placed
            by telegram users with quantity of product ordered greater than specified amount.
        """
        # aggregate join query grouped by telegram user id 
        # and filtered by quantity of product ordered.
        stmt = (
            select(func.sum(OrderProduct.quantity).label('quantity'), User.full_name.label('name'))
            .join(Order, Order.order_id == OrderProduct.order_id)
            .join(User)
            .group_by(User.telegram_id)
            .having(func.sum(OrderProduct.quantity) > greater_than)
        )

        # execute aggregate query.
        result = self._session.execute(stmt)

        # return sequence of fetched rows with aggregate result.
        return result.all()


if __name__ == "__main__":
    # url connection credentials set from environment file.
    env = Env()
    # specify path of environment file.
    env.read_env(path=".env")
    # connection url format: dialect+driver://username:password@host:port/database.
    url = URL.create(
        # driver name = postgresql + the library we are using
        drivername="postgresql+psycopg2", 
        username=env.str('POSTGRES_USER'),
        password=env.str('POSTGRES_PASSWORD'),
        host=env.str('DATABASE_HOST'),
        database=env.str('POSTGRES_DB'),
        port=env.int('PORT')
    )

    # connect to database engine
    engine = create_engine(
                url=url.render_as_string(hide_password=False),
                echo=True,
            )

    # a sessionmaker(), also in the same scope as the engine
    session_pool = sessionmaker(bind=engine)

    # we can now construct a session_pool()
    # without needing to pass the engine each time
    with session_pool() as session:
        # session.add(some_other_object)
        # create Repo instance.
        repo = Repo(session=session)

        # add an user instance to users table in database.
        """ repo.add_user(
            telegram_id=1,
            full_name='John Doe',
            language_code='en',
            username='Johnny',
            phone_number= '(123) 456-7890'
        )"""
 
        # select user instance added or updated in database.
        user_added = repo.add_user_combined(
                        telegram_id=2,
                        full_name='Juan Perez',
                        username='juanpe',
                        language_code='es',
                        phone_number='+34 123-4567',
                        referrer_id=1
                    )
        # display added user instance to database.
        """ if user_added:
            print(
                f'User: {user_added.telegram_id} ' +
                f'Full name: {user_added.full_name} ' +
                f'Username: {user_added.user_name} ' +
                f'Language code: {user_added.language_code} ' +
                f'Referrer id: {user_added.referrer_id}'
            ) """
    
        # fetch an user from database with given telegram_id.
        # user = repo.get_user_by_id(1)

        # display user details from database if found for given primary key identifier.
        """ if user:
            print(
                f'User: {user.telegram_id} ' +
                f'Full name: {user.full_name} ' +
                f'Username: {user.user_name} ' +
                f'Language code: {user.language_code} ' +
                f'Created at: {user.created_at}'
            ) """

        # fetch all users from users table in database.
        # users = repo.get_all_users()

        # display all users.
        # print(users)

        # fetch the language_code from user with provided telegram_id.
        # lang = repo.get_user_language_code(1)

        # display language_code of user if it exists.
        """ if user and lang:
            print(f"Language code of {user.full_name} is {lang}") """

        # fetch list of users filtered from database.
        # filtered_users = repo.get_all_users_advanced()

        # display users filtered from database.
        # print(filtered_users)

        # seed initial data fordatabase objects.
        repo.seed_fake_data()

        # fetch all invited users.
        for row in repo.select_all_invited_users():
            print(f"Parent: {row.parent_name}, Referral: {row.referral_name}")
        
        # fetch all users along with their orders and products ordered.
        for user in repo.get_all_users():
            print(f"User: {user.full_name} ({user.telegram_id})")
            for order in user.orders:
                print(f"    Order: {order.order_id}")
                for product in order.products:
                    print(f" Product: {product.product.title}")
        
        # fetch user orders.
        user_orders = repo.get_all_user_orders_user_full(telegram_id=2)

        # You have two ways of accessing retrieved orders of given user, 
        # first with tuple unpacking is like below:
        for order, user in user_orders:
            print(f'Order: {order.order_id} - {user.full_name}')
        print('=============')
        # Second is like next:
        for row in user_orders:
            print(f'Order: {row.Order.order_id} - {row.User.user_name}')
        print('=============')

        # In the next two examples you can see how to access your data when you
        # didn't specified full tables the right hand table is joined with user_name.
        user_orders = repo.get_all_user_orders_user_only_user_name(telegram_id=2653)

        # first with tuple unpacking is like below:
        for order, user_name in user_orders:
            print(f'Order: {order.order_id} - {user_name}')
        print('=============')
        for row in user_orders:
            # As you can see, if we specified column instead of full table, 
            # we can access it directly from row by using the name of column
            print(f'Order: {row.Order.order_id} - {row.user_name}')
        print('=============')

        # fetch all products and its quantity for orders made by given telegram user.
        product_orders_quant = repo.get_all_user_orders_relationships(telegram_id=2653)

        # display product and quantity for give order 
        # along with user_name that placed the order.
        # first with tuple unpacking is like below:
        for product, order, name, quantity in product_orders_quant:
            print(
                f"#{product.product_id} Product: {product.title} Quantity: {quantity} " +
                f"Order: {order.order_id}: {name}"
            )
        print('=============')

        # fetch all products and its quantity for orders made by given telegram user.
        product_orders_quant = repo.get_all_user_orders_no_relationships(telegram_id=2653)

        # display product and quantity for give order 
        # along with user_name that placed the order.
        # first with tuple unpacking is like below:
        for product, order, name, quantity in product_orders_quant:
            print(
                f"#{product.product_id} Product: {product.title} Quantity: {quantity} " +
                f"Order: {order.order_id}: {name}"
            )
        print('=============')

        # telegram user id.
        user_telegram_id = 2653

        # fetch aggregate result using sqlalchemy orm.
        user_total_number_of_orders = repo.get_user_total_number_of_orders(telegram_id=user_telegram_id)

        # display rows of user, total orders
        print(f'[User: {user_telegram_id}] total number of orders: {user_total_number_of_orders}')
        print('===========')

        # display rows of total orders, user id.
        for orders_count, telegram_id in repo.get_total_number_of_orders_by_user():
            print(f'Total number of orders: {orders_count} by {telegram_id}')
        print('===========')

        # display rows of orders with quarirt and user name.
        for row in repo.get_total_number_of_orders_by_user_with_labels():
            print(f'Total number of orders: {row.quantity} by {row.name}')
        print('===========')

        # display rows of quantity of products ordered by usr name.
        for products_count, name in repo.get_count_of_products_by_user():
            print(f'Total number of products: {products_count} by {name}')
        print('===========')

        # display rows of product quatity ordered by user name greater than given quantity. 
        for products_count, name in repo.get_count_of_products_greater_than_x_by_user(20_000):
            print(f'Total number of products: {products_count} by {name}')
        print('===========')

    # closes session after exiting the context manager.

