# -*- coding: utf-8 -*-

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

mysql_client = create_engine(
    "mysql+mysqlconnector://root:123456@127.0.0.1:3306/products?charset=utf8",
    encoding="utf-8",
)


session_sql = sessionmaker(bind=mysql_client)


@contextmanager
def session_scope():
    session = session_sql()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()