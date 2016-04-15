# -*- coding: utf-8 -*-
import os

import pytest
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy_defaults import make_lazy_configured


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
def lazy_configured(models):
    for model in models:
        make_lazy_configured(model.__mapper__)
