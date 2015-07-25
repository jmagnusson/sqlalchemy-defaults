# -*- coding: utf-8 -*-
import os
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy_defaults import make_lazy_configured

IS_MYSQL = (
    os.environ.get('DB') == 'mysql' or
    os.environ.get('DSN', '').startswith('mysql')
)
MYSQLD_VERSION = tuple(
    int(i) for i in
    os.popen('mysqld -V').read()
    .partition('Ver ')[2]
    .partition(' ')[0]
    .split('.')
    if i.isdigit()
)


def _get_default_settings_overrides():
    kw = {}
    if IS_MYSQL:
        # MySQL (at least up till version 5.7) does not support a default
        # value for TEXT type columns.
        kw['text_server_defaults'] = False

        if MYSQLD_VERSION:
            if MYSQLD_VERSION < (5, 7):
                # NOW() is not supported as a DEFAULT value below version 5.7
                kw['auto_now'] = False
    return kw


make_lazy_configured(
    sa.orm.mapper,
    **_get_default_settings_overrides()
)


class TestCase(object):
    def get_dsn_from_driver(self, driver):
        if driver == 'postgres':
            return 'postgres://postgres@localhost/sqlalchemy_defaults_test'
        elif driver == 'mysql':
            return 'mysql+pymysql://travis@localhost/sqlalchemy_defaults_test'
        elif driver == 'sqlite':
            return 'sqlite:///:memory:'
        else:
            raise Exception('Unknown driver given: %r' % driver)

    def setup_method(self, method):
        driver = os.environ.get('DB', 'sqlite')
        dsn = os.environ.get('DSN', None)
        if dsn is None:
            dsn = self.get_dsn_from_driver(driver)
        self.engine = create_engine(dsn)
        self.Model = declarative_base()

        self.create_models(**self.column_options)
        sa.orm.configure_mappers()
        if hasattr(self, 'User'):
            self.columns = self.User.__table__.c
        self.Model.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def teardown_method(self, method):
        self.session.close_all()
        self.Model.metadata.drop_all(self.engine)
        self.engine.dispose()
