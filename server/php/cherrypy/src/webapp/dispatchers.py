"""
Dispatchers implementing the MTT Server API.

Exports:
    Root: Root directoy
"""

#
# https://cherrypy.readthedocs.org/en/3.3.0/tutorial/REST.html
#

import pprint
import copy
import glob
import logging
import os
import json
import random
import string
import datetime

from subprocess import call

import cherrypy
from configobj import ConfigObj
from validate import Validator


#
# JSON serialization of datetime objects
#
class _JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        # timedelta does not have a isoformat
        elif isinstance(obj, datetime.timedelta):
            return str(obj).split('.',2)[0]
        return super().default(obj)

_json_encoder = _JSONEncoder()

def _json_handler(*args, **kwargs):
    # Adapted from cherrypy/lib/jsontools.py
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)

    return _json_encoder.iterencode(value)


class _ServerResourceBase:
    """Provide functionality needed by all resource dispatchers.

    Class Attrs:
        exposed (bool): If True, resource is accessible via the Web.

    Instance Attrs
        conf (ConfigObj): Application config object.
        logger (logging.Logger): Pre-configured application logging instance.
        api_root (str): URL of application's api root.
        url_base (str): Base URL for the resource.

    Methods:
        ...
    """

    exposed = True

    _db = None

    def __init__(self, conf):
        """Instantiate Server Resource.

        Args:
            conf (ConfigObj): Application configuration object.
        """
        self.conf = conf
        self.logger = logging.getLogger('onramp')

        server = None
        if 'url_docroot' in conf['server'].keys():
            server = conf['server']['url_docroot']
        else:
            server = conf['server']['socket_host'] + ':' + str(conf['server']['socket_port'])

        self.url_base = (server + '/' + self.__class__.__name__.lower() + '/')
        self.api_root = (server + '/api/')

        #
        # Define the Database connection - JJH TODO
        #
        self.logger.debug("Setup database connection")
        _db_settings = {}
        self._db = None

    def _not_implemented(self, prefix):
        self.logger.debug(prefix + " Not implemented")
        rtn = {}
        rtn['status'] = -1
        rtn['status_message'] = prefix + " Please implement this method..."
        return rtn

    def _return_error(self, prefix, code, msg):
        self.logger.debug(prefix + " Error ("+str(code)+") = " + msg)
        rtn = { "fields" : None,
                "values" : None,
                "timing" : 0 }
        rtn['status'] = code
        rtn['status_message'] = msg
        return rtn

########################################################
 

########################################################
# Root
########################################################
class Root(_ServerResourceBase):

    #
    # GET / : Server status
    #
    def GET(self, **kwargs):
        self.logger.debug('Root.GET()')
        return "MTT Server is running...\n"


########################################################
# Submit
########################################################
class Submit(_ServerResourceBase):

    #
    # POST /submit/:phase/
    #
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self, phase, **kwargs):
        prefix = '[POST /submit/'+str(phase)+']'
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'

        return self._not_implemented(prefix)
