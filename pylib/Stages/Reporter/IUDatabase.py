# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: f; python-indent: 4 -*-
#
# Copyright (c) 2015-2016 Intel, Inc. All rights reserved.
# $COPYRIGHT$
#
# Additional copyrights may follow
#
# $HEADER$
#

import os
import pwd
import requests
import json
import pprint
import re
from requests.auth import HTTPBasicAuth

from ReporterMTTStage import *

class IUDatabase(ReporterMTTStage):

    def __init__(self):
        # initialise parent class
        ReporterMTTStage.__init__(self)
        self.options = {}
        self.options['realm'] = (None, "Database name")
        self.options['username'] = (None, "Username to be used for submitting data")
        self.options['password'] = (None, "Password for that username")
        self.options['pwfile'] = (None, "File where password can be found")
        self.options['platform'] = (None, "Name of the platform (cluster) upon which the tests were run")
        self.options['hostname'] = (None, "Name of the hosts involved in the tests (may be regular expression)")
        self.options['url'] = (None, "URL of the database server")
        self.options['debug_filename'] = (None, "Debug output file for server interaction information")
        self.options['keep_debug_files'] = (False, "Retain reporter debug output after execution")
        self.options['debug_server'] = (False, "Ask the server to return its debug output as well")
        self.options['email'] = (None, "Email to which errors are to be sent")

    def activate(self):
        # get the automatic procedure from IPlugin
        IPlugin.activate(self)
        return


    def deactivate(self):
        IPlugin.deactivate(self)
        return

    def print_name(self):
        return "IUDatabase"

    def print_options(self, testDef, prefix):
        lines = testDef.printOptions(self.options)
        for line in lines:
            print prefix + line
        return

    def execute(self, log, keyvals, testDef):
        # parse the provided keyvals against our options
        cmds = {}
        testDef.parseOptions(log, self.options, keyvals, cmds)

        # quick sanity check
        sanity = 0
        if cmds['username'] is not None:
            sanity += 1
        if cmds['password'] is not None or cmds['pwfile'] is not None:
            sanity += 1
        if cmds['realm'] is not None:
            sanity += 1
        if 0 < sanity and sanity != 3:
            log['status'] = 1
            log['stderr'] = "MTTDatabase Reporter section",log['section'] + ": if password, username, or realm is specified, they all must be specified."
            return
        try:
            if cmds['pwfile'] is not None:
                if os.path.exists(cmds['pwfile'][0]):
                    f = open(cmds['pwfile'][0], 'r')
                    password = f.readline().strip()
                    f.close()
                else:
                    log['status'] = 1;
                    log['stderr'] = "Password file " + cmds['pwfile'][0] + " does not exist"
                    return
			elif cmds['password'] is not None:
				password = cmds['password']
        except KeyError:
            try:
                if cmds['password'] is not None:
                    password = cmds['password'][0]
            except KeyError:
                pass
		#
        # Setup the JSON data structure
		#
        s = requests.Session()
		url = cmds['url'] + "/submit"
        if 0 < sanity:
			www_auth = HTTPBasicAuth(cmds['username'], password)
		else:
			www_auth = None

		# Get a client serial number
		client_serial = self._get_client_serial(s, cmds['url'], www_auth)
		if client_serial < 0:
			print "Error: Unable to get a client serial (rtn=%d)" % (client_serial)

        headers = {}
        headers['content-type'] = 'application/json'

		data = {}

		profile = testDef.logger.getLog('Profile:Installed')
		metadata = {}
		metadata['client_serial'] = client_serial
		metadata['hostname'] = profile['profile']['nodeName']
		metadata['http_username'] = cmds['username']
		metadata['local_username'] = pwd.getpwuid(os.getuid()).pw_name
		metadata['mtt_client_version'] = '4.0a1'
		metadata['platform_name'] = self._extract_param(testDef.logger, 'MTTDefaults', 'platform')
		metadata['trial'] = int(self._extract_param(testDef.logger, 'MTTDefaults', 'trial'))

		# Strategy:
		# For each Test Run section
		#  - Find 'parent' Test Build
		#    - Find 'middleware' MiddlewareBuild (MPI Install)
		#      - Submit MPI Install phase
		#    - Submit Test Build phase
		#  - for each test run result
		#    - Submit Test Run phase

        # get the entire log of results
        fullLog = testDef.logger.getLog(None)
		pp = pprint.PrettyPrinter(indent=4)

		#
		# Dump the entire log
		#
		print "<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>"
        for lg in fullLog:
			print "----------------- Section (%s) " % (lg['section'])
			pp.pprint(lg)
		print "<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>"

		#
		# Process the test run sections
		#
        for lg in fullLog:
			# Find sections prefixed with 'TestRun'
			if re.match("TestRun", lg['section']):
				rtn = self._submit_test_run(testDef.logger, lg, metadata, s, url, www_auth)

        log['status'] = 0
        return

	def _merge_dict(self, x, y):
		z = x.copy()
		z.update(y)
		return z

	def _submit_test_run(self, logger, lg, metadata, s, url, httpauth=None):
		print "----------------- Test Run (%s) " % (lg['section'])

		pp = pprint.PrettyPrinter(indent=4)
		pp.pprint(lg)

		# Find 'parent' Test Build - submit
		test_info = self._submit_test_build(logger,
									  logger.getLog(self._extract_param(logger, lg['section'], 'parent')),
									  metadata,
									  s, url, httpauth)
		if test_info is None:
			return None

		#
		# Prepare to submit
		# JJH Todo fill these fields in
		#
		metadata['phase'] = 'Test Run'

		common_data = {}
		common_data['mpi_install_id'] = None
		common_data['test_build_id'] = None

		for trun in testresults:
			data = {}

			data['mpi_install_id'] = common_data['mpi_install_id']
			data['test_build_id'] = common_data['test_build_id']

			data['launcher'] = None
			data['resource_manager'] = None
			data['parameters'] = None
			data['network'] = None

			data['test_name'] = None
			data['np'] = None
			data['full_command'] = None

			data['start_timestamp'] = None
			data['duration'] = None

			data['result_message'] = None
			data['test_result'] = None
			data['exit_value'] = None
			data['exit_signal'] = None
			
			# Optional
			data['latency_bandwidth'] = None
			data['message_size'] = None
			data['latency_min'] = None
			data['latency_avg'] = None
			data['latency_max'] = None
			data['bandwidth_min'] = None
			data['bandwidth_avg'] = None
			data['bandwidth_max'] = None
			data['description'] = None
			data['environment'] = None
			data['merge_stdout_stderr'] = None
			data['result_stdout'] = None
			data['result_stderr'] = None

			#
			# Submit
			#
			payload = {}
			payload['metadata'] = metadata
			payload['data'] = [data]

			data = self._submit_json_data(payload, s, url, httpauth)
			if data is None:
				return None
			if data['status'] is not 0:
				return None

		return True

	def _submit_test_build(self, logger, lg, metadata, s, url, httpauth=None):
		print "----------------- Test Build (%s) " % (lg['section'])

		pp = pprint.PrettyPrinter(indent=4)
		pp.pprint(lg)

		# Find 'parent' Test Get (not needed)
		# Find 'middleware' MiddlewareBuild (MPI Install)
		install_info = self._submit_install(logger,
								   logger.getLog(self._extract_param(logger, lg['section'], 'middleware')),
								   metadata,
								   s, url, httpauth)
		if install_info is None:
			return None

		#
		# Prepare to submit
		# JJH Todo fill these fields in
		#
		data = {}
		metadata['phase'] = 'Test Build'

		data['mpi_install_id'] = None

		data['compiler_name'] = None
		data['compiler_version'] = None

		data['suite_name'] = None

		data['start_timestamp'] = None
		data['duration'] = None

		data['result_message'] = None
		data['test_result'] = None
		data['exit_value'] = None
		data['exit_signal'] = None

		# Optional
        data['description'] = None
		data['environment'] = None
		data['merge_stdout_stderr'] = None
		data['result_stdout'] = None
		data['result_stderr'] = None

		#
		# Submit
		#
        payload = {}
		payload['metadata'] = metadata
		payload['data'] = [data]

		data = self._submit_json_data(payload, s, url, httpauth)
		if data is None:
			return None
		if data['status'] is not 0:
			return None

		# Extract ID
		return self._merge_dict( {'test_build_id':data['ids']['test_build_id']},
								 install_info)

	def _submit_install(self, logger, lg, metadata, s, url, httpauth=None):
		print "----------------- MPI Install (%s) " % (lg['section'])
		pp = pprint.PrettyPrinter(indent=4)
		pp.pprint(lg)

		# Find 'parent' MiddlewareGet (MPI Get) (not needed?)

		#
		# Prepare to submit
		# JJH Todo fill these fields in
		#
		data = {}
		metadata['phase'] = 'MPI Install'

		data['platform_hardware'] = None
		data['platform_type'] = None

		data['os_name'] = None
		data['os_version'] = None

		data['compiler_name'] = None
		data['compiler_version'] = None

		data['mpi_name'] = None
		data['mpi_version'] = None

		data['vpath_mode'] = None
		data['bitness'] = None
		data['endian'] = None

		data['configure_arguments'] = None
		data['start_timestamp'] = None
		data['duration'] = None

		data['result_message'] = None
		data['test_result'] = None
		data['exit_value'] = None
		data['exit_signal'] = None

		# Optional
        data['description'] = None
		data['environment'] = None
		data['merge_stdout_stderr'] = None
		data['result_stdout'] = None
		data['result_stderr'] = None

		#
		# Submit
		#
        payload = {}
		payload['metadata'] = metadata
		payload['data'] = [data]

		data = self._submit_json_data(payload, s, url, httpauth)
		if data is None:
			return None
		if data['status'] is not 0:
			return None

		# Extract ID
		return {'mpi_install_id':data['ids']['mpi_install_id']}

	def _submit_json_data(self, payload, s, url, httpauth=None):
        headers = {}
        headers['content-type'] = 'application/json'

        print "<<<<<<<---------------- Payload (Start) -------------------------->>>>>>"
		print json.dumps(payload, sort_keys=True, indent=4, separators=(',',': '))
        print "<<<<<<<---------------- Payload (End  ) -------------------------->>>>>>"

		r = s.post(url,
				   data=json.dumps(payload),
				   headers=headers, 
				   auth=httpauth,
				   verify=False)

        print "<<<<<<<---------------- Response -------------------------->>>>>>"
        print "Result: %d: %s" % (r.status_code, r.headers['content-type'])
        print r.headers
        print r.reason
        print "<<<<<<<---------------- Raw Output (Start) ---------------->>>>>>"
        print r.text
        print "<<<<<<<---------------- Raw Output (End  ) ---------------->>>>>>"

		if r.status_code != 200:
			return None

		return r.json()

	def _extract_param(self, logger, section, parameter):
		found = logger.getLog(section)
		if found is None:
			print "_extract_param: Section (%s) Not Found! [param=%s]" % (section, parameter)
			return None

		params = found['parameters']
		for p in params:
			if p[0] == parameter:
				return p[1]

	def _get_client_serial(self, session, url, httpauth=None):
		url = url + "/serial"

        headers = {}
        headers['content-type'] = 'application/json'

		payload = {}
		payload['serial'] = 'serial'

		data = self._submit_json_data(payload, session, url, httpauth)
		if data is None:
			return -1

		if data['status'] is not 0:
			return -2

		return data['client_serial']
