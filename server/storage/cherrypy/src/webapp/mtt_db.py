"""Functionality to support interacting with various MTT Databases

"""
import os
import json
import exceptions

##########################################
# Interface class that all Databases must implement
##########################################
class Database():
    def __init__(self, logger, auth):
        self._auth = auth
        self._logger = logger

    ##########################################################
    def is_available(self):
        raise NotImplemented("Please implement this method")

    ##########################################################
    def is_connected(self):
        raise NotImplemented("Please implement this method")

    def connect(self):
        raise NotImplemented("Please implement this method")

    def disconnect(self):
        raise NotImplemented("Please implement this method")

    ##########################################################
    def which_table_contains(self, col):
        raise NotImplemented("Please implement this method")

    def run_summary(self, session=[], data=[]):
        raise NotImplemented("Please implement this method")

    def run_detail(self, session=[], data=[]):
        raise NotImplemented("Please implement this method")

    ##########################################################

from webapp.mtt_db_pg_flat import Database_pg_flat


##########################################
# Accessor class to the backend database
# - Caller does not need to worry about connecting/disconnecting or SQL
# - Caller invokes operations on the data
##########################################
class DBAccess():
    _known_db = { 'pg_flat' : Database_pg_flat }

    ##########################################
    def __init__(self, logger, dbtype, auth):
        self._logger = logger
        if dbtype not in self._known_db:
            self._logger.critical( "Database: \"%s\" is not supported." % (dbtype) )
            raise NotImplementedError

        self._db = self._known_db[dbtype](logger, auth)

    ##########################################
    def is_available(self):
        return self._db.is_available()

    ##########################################
    def which_table_contains(self, col):
        return self._db.which_table_contains(col)

    def run_summary(self, session=[], data=[]):
        self._db.connect()
        (rows, fields) = self._db.run_summary(session, data)
        self._db.disconnect()

        return (rows, fields)

    def run_detail(self, session=[], data=[]):
        self._db.connect()
        (rows, fields) = self._db.run_detail(session, data)
        self._db.disconnect()

        return (rows, fields)

    ##########################################
