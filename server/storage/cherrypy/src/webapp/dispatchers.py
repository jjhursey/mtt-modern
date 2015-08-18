"""Dispatchers implementing the MTT Server API.

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
import hashlib
import shutil
from multiprocessing import Process
from subprocess import call

import cherrypy
from configobj import ConfigObj
from Crypto import Random
from Crypto.Cipher import AES
from validate import Validator

import random
import string
import datetime

#import webapp.onrampdb as onrampdb
import webapp.summary
import webapp.detail

class _ServerResourceBase:
    """Provide functionality needed by all MTT Server resource dispatchers.

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
    _db_settings = {}

    def __init__(self, conf):
        """Instantiate MTT Server Resource.

        Args:
            conf (ConfigObj): Application configuration object.
        """
        # Define the configuration and logger channel
        self.conf = conf
        self.logger = logging.getLogger('mtt')

        # URL generation prefix string
        server = None
        if 'url_docroot' in conf['server'].keys():
            server = conf['server']['url_docroot']
        else:
            server = conf['server']['socket_host'] + ':' + str(conf['server']['socket_port'])

        self.url_base = (server + '/' + self.__class__.__name__.lower() + '/')
        self.api_root = (server + '/api/')

        #
        # Define the Database - JJH TODO
        #
        self.logger.debug("Setup database credentials")
        #self._db = onrampdb.DBAccess(self.logger, 'sqlite', {'filename' : os.getcwd() + '/../tmp/onramp_sqlite.db'} )
        #if self._db is None:
        #    sys.exit(-1)
        # JJH do not hardcode the section
        section = "mttflat"
        for option in conf[section]:
            try:
                self._db_settings[option] = conf.get( section, option)
                if self._db_settings[option] == -1 :
                    DebugPrint("Skipping option: %s" % option)
            except:
                print("Exception on %s!" % option)
                self._db_settings[option] = None

        #
        # Check settings for DB connection
        #
        self.logger.debug("-" * 70)
        self.logger.debug("Check settings")
        rtn_msg = self._check_settings()


    def _check_settings(self):
        if None == self._db_settings.get("type") or None == self._db_settings["type"]:
            return "Error: Configuration settings missing the \"type\" field"
        if None == self._db_settings.get("dbname") or None == self._db_settings["dbname"]:
            return "Error: Configuration settings missing the \"dbname\" field"
        if None == self._db_settings.get("username") or None == self._db_settings["username"]:
            return "Error: Configuration settings missing the \"username\" field"
        if None == self._db_settings.get("password") or None == self._db_settings["password"]:
            return "Error: Configuration settings missing the \"password\" field"
        return None


    def _not_implemented(self, prefix):
        self.logger.debug(prefix + " Not implemented")
        rtn = {}
        rtn['status'] = -1
        rtn['status_message'] = prefix + " Please implement this method..."
        return rtn

    def _return_error(self, prefix, code, msg):
        self.logger.debug(prefix + " Error ("+str(code)+") = " + msg)
        rtn = {}
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
        prefix = '[GET /]'
        self.logger.debug(prefix)

        # html = """<html>
        #    <head>
        #      <title>MTT Storage Welcome Page</title>
        #    </head>
        #    <body>
        #      <h2>Welcome ot the MTT Storage service welcome page!</h2>
        #      <p>
        #      If you know your party's extension enter the URL at any time.
        #      If not then consult the documentation.
        #      </p>
        #      <ul>
        #        <li>Server Fields: <a href=\"fields\">Click here</a>
        #        <li>Summary Views: <a href=\"summary\">Click here</a>
        #        <li>Detail Views: <a href=\"detail\">Click here</a>
        #        <li>
        #      </ul>
        #    </body>
        #    </html>"""
        # return html

        return "MTT Server is running...\n"


########################################################
# Fields
########################################################
class Fields(_ServerResourceBase):

    #
    # GET /fields
    # GET /fields/$phase
    #
    @cherrypy.tools.json_out()
    def GET(self, phase="all", **kwargs):
        prefix = '[GET /fields]'
        self.logger.debug(prefix)

        return summary.fields(self._db_settings, cherrypy.session);

########################################################
# Summary
########################################################
class Summary(_ServerResourceBase):

    #
    # GET /summary
    # GET /summary/$phase
    #
    @cherrypy.tools.json_out()
    def GET(self, phase="all", **kwargs):
        prefix = '[GET /summary]'
        self.logger.debug(prefix)

        data = {}
        start_time = datetime.datetime.now()
        end_time = datetime.datetime.now()

        self.logger.debug("m" * 80)
        self.logger.debug("m" * 80)
        self.logger.debug("m" * 80)
        self.logger.debug("mmmm  New Summary Request")
        self.logger.debug("m" * 80)

        self.logger.debug("----------------------")
        pp = pprint.PrettyPrinter(indent=4)
        self.logger.debug(pp.pformat(cherrypy.request.headers))
        self.logger.debug("----------------------")

        self.logger.debug("-" * 70)
        self.logger.debug("Preprocess parameters")

        #
        # If they sent JSON data, then use that
        #
        if hasattr(cherrypy.request, "json"):
            data = cherrypy.request.json
            if "phases" not in data:
                rtn = { "fields" : None, "values" : None, "timing" : str(datetime.datetime.now() - start_time) }
                rtn['status'] = -1
                rtn['status_msg'] = "Error: Parameter 'phases' not supplied."
                return rtn
            if len(data["phases"]) == 0:
                phases = []
                phases.append( "all" )
                data["phases"] = phases
            elif type(data["phases"]) is not list:
                phases = []
                phases.append( data["phases"] )
                data["phases"] = phases
            else:
                phases = data["phases"]
            self.logger.debug("Type: %s" %( type(data["phases"]) ) )
            self.logger.debug("(All) = " + json.dumps(data, sort_keys=True, indent=4, separators=(',',': ')))
        # Otherwise build it from the parameters
        else:
            self.logger.debug("Not a JSON Request")
            data["phases"] = phases
            
        self.logger.debug("(Phase) = \""+ ",".join(phases) +"\"")
        
        cherrypy.session['phases'] = phases

        #
        # Validate the search parameters
        #
        self.logger.debug("-" * 70)
        self.logger.debug("Validate Parameters")
        rtn = summary.validate_search_parameters(self._db_settings, cherrypy.session, data)
        if rtn['status'] != 0:
            self.logger.debug("Validate Failed:")
            self.logger.debug("Returned: " + str(rtn['status']) + ") " + rtn['status_msg'])
            return rtn
        
        #
        # Perform the search
        #
        self.logger.debug("-" * 70)
        self.logger.debug("Perform search")
        rtn = summary.index(self._db_settings, cherrypy.session, data)
        
        rtn['status'] = 0
        rtn['status_msg'] = 'Success'
        rtn['timing'] = str(datetime.datetime.now() - start_time)

        #self.logger.debug("(Final) " + json.dumps(rtn, sort_keys=True, indent=4, separators=(',',': ')))
        
        return rtn;


########################################################
# Detail
########################################################
class Detail(_ServerResourceBase):

    #
    # GET /detail
    # GET /detail/$phase
    #
    @cherrypy.tools.json_out()
    def GET(self, phase="all", **kwargs):
        prefix = '[GET /detail]'
        self.logger.debug(prefix)

        data = {}
        start_time = datetime.datetime.now()
        end_time = datetime.datetime.now()

        self.logger.debug("m" * 80)
        self.logger.debug("m" * 80)
        self.logger.debug("m" * 80)
        self.logger.debug("mmmm  New Detail Request")
        self.logger.debug("m" * 80)

        self.logger.debug("----------------------")
        pp = pprint.PrettyPrinter(indent=4)
        self.logger.debug(pp.pformat(cherrypy.request.headers))
        self.logger.debug("----------------------")

        self.logger.debug("-" * 70)
        self.logger.debug("Preprocess parameters")

        #
        # If they sent JSON data, then use that
        #
        if hasattr(cherrypy.request, "json"):
            data = cherrypy.request.json
            if "phases" not in data:
                rtn = { "fields" : None, "values" : None, "timing" : str(datetime.datetime.now() - start_time) }
                rtn['status'] = -1
                rtn['status_msg'] = "Error: Parameter 'phases' not supplied."
                return rtn
            if len(data["phases"]) == 0:
                phases = []
                phases.append( "all" )
                data["phases"] = phases
            elif type(data["phases"]) is not list:
                phases = []
                phases.append( data["phases"] )
                data["phases"] = phases
            else:
                phases = data["phases"]
            self.logger.debug("Type: %s" %( type(data["phases"]) ) )
            self.logger.debug("(All) = " + json.dumps(data, sort_keys=True, indent=4, separators=(',',': ')))
        # Otherwise build it from the parameters
        else:
            self.logger.debug("Not a JSON Request")
            data["phases"] = phases
            
        self.logger.debug("(Phase) = \""+ ",".join(phases) +"\"")
        
        cherrypy.session['phases'] = phases

        #
        # Validate the search parameters
        #
        self.logger.debug("-" * 70)
        self.logger.debug("Validate Parameters")
        rtn = summary.validate_search_parameters(self._db_settings, cherrypy.session, data, False)
        if rtn['status'] != 0:
            self.logger.debug("Validate Failed:")
            self.logger.debug("Returned: " + str(rtn['status']) + ") " + rtn['status_msg'])
            return rtn
        
        #
        # Perform the search
        #
        self.logger.debug("-" * 70)
        self.logger.debug("Perform search")
        rtn = detail.index(self._db_settings, cherrypy.session, data)

        #
        # Shape up the output header
        #
        rtn['status'] = 0
        rtn['status_msg'] = 'Success'
        rtn['timing'] = str(datetime.datetime.now() - start_time)

        return rtn;

########################################################
