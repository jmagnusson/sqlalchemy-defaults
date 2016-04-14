# -*- coding: utf-8 -*-
import os

import pytest
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy_defaults import make_lazy_configured

from . import IS_MYSQL, MYSQLD_VERSION


@pytest.fixture(scope='session')
def dsn():
    return os.environ.get('DSN') or 'sqlite:///:memory:'


@pytest.fixture
def Base():
    return declarative_base()


@pytest.yield_fixture
def engine(dsn):
    engine = create_engine(dsn)
    yield engine
    engine.dispose()


@pytest.fixture
def models():
    return []


@pytest.fixture
def lazy_options():
    return {}


@pytest.yield_fixture
def Session(Base, engine, models):
    sa.orm.configure_mappers()
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine)
    Base.metadata.drop_all(engine)


@pytest.yield_fixture
def session(Session):
    session = Session()
    yield session
    session.close_all()


@pytest.fixture
def default_options():
    opts = {}
    if IS_MYSQL:
        # MySQL (at least up till version 5.7) does not support a default
        # value for TEXT type columns.
        opts['text_server_defaults'] = False

        if MYSQLD_VERSION:
            if MYSQLD_VERSION < (5, 7):
                # NOW() is not supported as a DEFAULT value below version 5.7
                opts['auto_now'] = False
    return opts


@pytest.fixture
def lazy_configured(default_options, models, session):
    for model in models:
        make_lazy_configured(
            sa.orm.mapper,
            **default_options
        )
