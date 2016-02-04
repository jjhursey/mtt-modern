"""Support for PostgreSQL database 'v3'
"""

import os
import mtt_db

import pprint
import psycopg2
import string
import re
from threading import Lock

#################################################################
# Interface to the database
#################################################################
class Database_pg_v3( mtt_db.Database ):
    _name = '[DB PG V3]'
    _lock = Lock()

    def __init__(self, logger, auth):
        mtt_db.Database.__init__(self, logger, auth)
        self._auth = auth

        self._connection = None
        self._refcount = 0


    ##########################################################
    def is_available(self):
        if None == self._auth.get("type") or None == self._auth["type"]:
            self._logger.error(self._name + "Error: Configuration settings missing the \"type\" field")
            return False
        if None == self._auth.get("dbname") or None == self._auth["dbname"]:
            self._logger.error(self._name + "Error: Configuration settings missing the \"dbname\" field")
            return False
        if None == self._auth.get("username") or None == self._auth["username"]:
            self._logger.error(self._name + "Error: Configuration settings missing the \"username\" field")
            return False
        if None == self._auth.get("password") or None == self._auth["password"]:
            self._logger.error(self._name + "Error: Configuration settings missing the \"password\" field")
            return False
        return True

    ##########################################################
    def is_connected(self):
        if self._connection is not None:
            return True
        else:
            return False

    def connect(self):
        if self._refcount > 0:
            self._logger.error(self._name + " connect while refcount > 0 (" + str(self._refcount) + ") zzzzzzzzzzzzzzzzz")
            return

        conn_str = ("dbname=" +    str(self._auth["dbname"]) +
                    " user=" +     str(self._auth["username"]) +
                    " password="+ str(self._auth["password"]) +
                    " host="+     str(self._auth["server"]) +
                    " port="+     str(self._auth["port"]) )
        self._connection = psycopg2.connect( conn_str )


    def disconnect(self):
        if self._refcount > 0:
            self._logger.error(self._name + " disconnect while refcount > 0 (" + str(self._refcount) + ") zzzzzzzzzzzzzzzzz")
            return

        self._connection.close()
        self._connection = None

    # Open/Close a per-thead cursor
    def _open_database_cursor(self):
        return self._connection.cursor()

    def _close_databsse_cursor(self, cursor):
        cursor.close()
        return None

    ##########################################################
    def which_table_contains(self, field):
        tables = []
        return tables

    def run_summary(self, session=[], data=[]):
        return None, None

    def run_detail(self, session=[], data=[]):
        return None, None

    def get_testsuite(self, session=[], data=[]):
        return None, None

    def get_runtime(self, session=[], data=[]):
        return None, None


    ##########################################################
    # Internal functionality
    ##########################################################

