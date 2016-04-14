# -*- coding: utf-8 -*-
import os

IS_MYSQL = os.environ.get('DSN', '').startswith('mysql')
MYSQLD_VERSION = tuple(
    int(i) for i in
    os.popen('mysqld -V').read()
    .partition('Ver ')[2]
    .partition(' ')[0]
    .split('.')
    if i.isdigit()
)
