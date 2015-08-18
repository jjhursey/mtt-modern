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

import webapp.mtt_db as mttdb
import webapp.check as check

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
        self.logger.debug("Setup database connection")
        _db_settings = {}

        section = "pg_flat"
        _db_settings = conf[section]

        # Get a handle for the DB, and make sure it is available
        self._db = mttdb.DBAccess(self.logger, section, _db_settings)
        if self._db is None or self._db.is_available() is False:
            sys.exit(-1)


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

        rtn = { "summary": {
                "http_username"       : "Org",
                "local_username"      : "Local username",
                "platform_name"       : "Platform name",
                "platform_hardware"   : "Hardware",
                "os_name"             : "OS",
                "mpi_name"            : "MPI name",
                "mpi_version"         : "MPI version",
                "os_version"          : "OS version",
                "platform_type"       : "Platform type",
                "hostname"            : "Hostname",
                "compiler_name"       : "Compiler",
                "compiler_version"    : "Compiler version",
                "vpath_mode"          : "Vpath mode",
                "endian"              : "Endian",
                "bitness"             : "Bitness",
                "exit_value"          : "Exit value",
                "exit_signal"         : "Signal",
                "duration"            : "Duration",
                "np"                  : "np",
                "test_suite_name"     : "Test Suite",
                "test_name"           : "Test",
                "compute_cluster"     : "Cluster",
                "trial"               : "Trial",
                "all_phases"          : "All phases",
                "mpi_get"             : "MPI get",
                "mpi_install"         : "MPI install",
                "mpi_install_pass"    : "MPI install Pass",
                "mpi_install_fail"    : "MPI install Fail",
                "test_build"          : "Test build",
                "test_build_pass"     : "Test build Pass",
                "test_build_fail"     : "Test build Fail",
                "test_run"            : "Test run",
                "test_run_pass"       : "Test run Pass",
                "test_run_fail"       : "Test run Fail",
                "test_run_skip"       : "Test run Skip",
                "test_run_timed"      : "Test run Timed",
                "test_run_perf"       : "Test run Perf"
                },
                "detail": {
                "full_command"        : "Command",
                "configure_arguments" : "Configure arguments",
                "description"         : "Description",
                "launcher"            : "Launcher",
                "resource_mgr"        : "Resource Manager",
                "parameters"          : "Runtime Parameters",
                "network"             : "Network",
                "result_message"      : "Result message",
                "result_stderr"       : "Stderr",
                "result_stdout"       : "Stdout",
                "merge_stdout_stderr" : "Merge stdout stderr",
                "start_timestamp"     : "Date range",
                "environment"         : "Environment",
                "bandwidth_avg"       : "Bandwidth avg.",
                "bandwidth_max"       : "Bandwidth max.",
                "bandwidth_min"       : "Bandwidth min.",
                "latency_avg"         : "Latency avg.",
                "latency_max"         : "Latency max.",
                "latency_min"         : "Latency min.",
                "message_size"        : "Message size",
                "message_size_range"  : "Message sizes",
                "mtt_version_major"   : "MTT version major",
                "mtt_version_minor"   : "MTT version minor",
                "mtt_client_version"  : "MTT version",
                "submit_timestamp"    : "Date range",
                "test_result"         : "Test result",
                "username"            : "Username",
                "value"               : "Value"
                },
                "unsorted": {
                "submit"            : "Submit",
                "results"           : "Results",
                "_mpi_p"            : "pass",
                "_mpi_f"            : "fail",
                "_build_p"          : "pass",
                "_build_f"          : "fail",
                "_run_p"            : "pass",
                "_run_f"            : "fail",
                "_run_s"            : "skipped",
                "_run_t"            : "timed_out",
                "_run_l"            : "latency_bandwidth",
                "pass"              : "Pass",
                "fail"              : "Fail",
                "skip"              : "Skip",
                "timed"             : "Timed",
                "skipped"           : "Skip",
                "timed_out"         : "Timed",
                "latency_bandwidth" : "Perf",
                "latency_avg"       : "Average Latency",
                "latency_min"       : "Minimum Latency",
                "latency_max"       : "Maximum Latency",
                "bandwidth_avg"     : "Average Bandwidth",
                "bandwidth_min"     : "Minimum Bandwidth",
                "bandwidth_max"     : "Maximum Bandwidth"
                }
                }

          #     "adv_cluster": {
          #   "os_version"          : "OS version",
          #   "platform_type"       : "Platform type"
          # },
          # "adv_mpi_install": {
          #   "compiler_name"       : "Compiler",
          #   "compiler_version"    : "Compiler version",
          #   "vpath_mode"          : "Vpath mode",
          #   "endian"              : "Endian",
          #   "bitness"             : "Bitness",
          #   "configure_arguments" : "Configure arguments"
          # },
          # "adv_test_build": {
          #   "todo"            : "Todo",
          #   "todo2"           : "Todo 2"
          # },
          # "adv_test_run": {
          #   "todo"            : "Todo",
          #   "todo2"           : "Todo 2"
          # },

        return rtn

########################################################
# Summary
########################################################
class Summary(_ServerResourceBase):

    #
    # POST /summary
    #
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self, **kwargs):
        prefix = '[GET /summary]'
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'

        # Make sure they sent JSON data
        if not hasattr(cherrypy.request, "json"):
            self.logger.error(prefix + " No json data sent")
            raise cherrypy.HTTPError(400)

        data = cherrypy.request.json
        start_time = datetime.datetime.now()
        end_time = datetime.datetime.now()


        self.logger.debug("m" * 80)
        self.logger.debug("m" * 80)
        self.logger.debug("mmmm  New Summary Request")
        self.logger.debug("m" * 80)
        self.logger.debug("m" * 80)
        pp = pprint.PrettyPrinter(indent=4)
        self.logger.debug("(Headers) = \n"+pp.pformat(cherrypy.request.headers))
        self.logger.debug("m" * 80)
        self.logger.debug("(Data) = \n" + json.dumps(data, sort_keys=True, indent=4, separators=(',',': ')))
        self.logger.debug("m" * 80)

        self.logger.debug("-" * 70)
        self.logger.debug("Preprocess parameters")

        #
        # Determine the 'phases'
        #
        phases = []
        if "phases" not in data:
            return self._return_error(prefix, -1, "Error: Parameter 'phases' not supplied.")
        if len(data["phases"]) == 0:
            phases.append( "all" )
            data["phases"] = phases
        elif type(data["phases"]) is not list:
            phases.append( data["phases"] )
            data["phases"] = phases
        else:
            phases = data["phases"]

        self.logger.debug("Type: %s" %( type(data["phases"]) ) )
        self.logger.debug("(Phase) = \""+ ",".join(phases) +"\"")
        
        cherrypy.session['phases'] = phases

        #
        # Validate the search parameters
        #
        self.logger.debug("-" * 70)
        self.logger.debug("Validate Parameters")
        rtn = check.validate_search_parameters(self._db, self.logger, cherrypy.session, data)
        if rtn['status'] != 0:
            self.logger.error("Validate Failed:")
            self.logger.error("Returned: " + str(rtn['status']) + ") " + rtn['status_msg'])
            return rtn
        
        #
        # Perform the search
        #
        self.logger.debug("-" * 70)
        self.logger.debug("Perform search")
        fields = ["http_username",
                  "platform_name",
                  "platform_hardware",
                  "os_name",
                  "mpi_name",
                  "mpi_version",
                  "mpi_install_pass",
                  "mpi_install_fail",
                  "test_build_pass",
                  "test_build_fail",
                  "test_run_pass",
                  "test_run_fail",
                  "test_run_skip",
                  "test_run_timed",
                  "test_run_perf"]

        rows, fields = self._db.run_summary(cherrypy.session, data)
        if rows is None:
            rtn = { "fields" : fields, "values" : None }
        else:
            rtn = { "fields" : fields, "values" : rows }

        #
        # Build the response
        #
        self.logger.debug("Returning: " + str(len(rows)) + " values (rows)")
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
    # POST /detail
    # POST /detail/$phase
    #
    #
    # POST /summary
    #
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self, **kwargs):
        prefix = '[GET /detail]'
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'

        # Make sure they sent JSON data
        if not hasattr(cherrypy.request, "json"):
            self.logger.error(prefix + " No json data sent")
            raise cherrypy.HTTPError(400)

        data = cherrypy.request.json
        start_time = datetime.datetime.now()
        end_time = datetime.datetime.now()


        self.logger.debug("m" * 80)
        self.logger.debug("m" * 80)
        self.logger.debug("mmmm  New Detail Request")
        self.logger.debug("m" * 80)
        self.logger.debug("m" * 80)
        pp = pprint.PrettyPrinter(indent=4)
        self.logger.debug("(Headers) = \n"+pp.pformat(cherrypy.request.headers))
        self.logger.debug("m" * 80)
        self.logger.debug("(Data) = \n" + json.dumps(data, sort_keys=True, indent=4, separators=(',',': ')))
        self.logger.debug("m" * 80)

        self.logger.debug("-" * 70)
        self.logger.debug("Preprocess parameters")

        #
        # Determine the 'phases'
        #
        phases = []
        if "phases" not in data:
            return self._return_error(prefix, -1, "Error: Parameter 'phases' not supplied.")
        elif len(data["phases"]) != 1:
            return self._return_error(prefix, -1, "Error: Parameter 'phases' must contain only one option.")
        elif type(data["phases"]) is not list:
            phases.append( data["phases"] )
            data["phases"] = phases
        else:
            phases = data["phases"]

        if phases[0] not in {"install", "test_build", "test_run"}:
            return self._return_error(prefix, -1, "Error: Parameter 'phases' unsupported \""+phases[0]+"\".")

        self.logger.debug("Type: %s (%d)" %( type(data["phases"]), len(data["phases"]) ) )
        self.logger.debug("(Phase) = \""+ ",".join(phases) +"\"")
        
        cherrypy.session['phases'] = phases

        #
        # Validate the search parameters
        #
        self.logger.debug("-" * 70)
        self.logger.debug("Validate Parameters")
        rtn = check.validate_search_parameters(self._db, self.logger, cherrypy.session, data)
        if rtn['status'] != 0:
            self.logger.error("Validate Failed:")
            self.logger.error("Returned: " + str(rtn['status']) + ") " + rtn['status_msg'])
            return rtn
        
        #
        # Perform the search
        #
        self.logger.debug("-" * 70)
        self.logger.debug("Perform search")
        fields = ["http_username",
                  "platform_name",
                  "platform_hardware",
                  "os_name",
                  "mpi_name",
                  "mpi_version",
                  "compiler_name",
                  "vpath_mode",
                  "compiler_version",
                  "configure_arguments",
                  "description",
                  "exit_value",
                  "exit_signal",
                  "result_message",
                  "result_stdout",
                  "result_stderr",
                  "environment"
                  ]

        rows, fields = self._db.run_detail(cherrypy.session, data)
        if rows is None:
            rtn = { "fields" : fields, "values" : None }
        else:
            rtn = { "fields" : fields, "values" : rows }

        #
        # Build the response
        #
        self.logger.debug("Returning: " + str(len(rows)) + " values (rows)")
        rtn['status'] = 0
        rtn['status_msg'] = 'Success'
        rtn['timing'] = str(datetime.datetime.now() - start_time)

        #self.logger.debug("(Final) " + json.dumps(rtn, sort_keys=True, indent=4, separators=(',',': ')))
        
        return rtn;


########################################################
