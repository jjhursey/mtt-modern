#!src/env/bin/python

"""Initialize and launch the MTT Server REST server."""

import logging
import os
import signal
import socket
import sys

import cherrypy
from cherrypy.process.plugins import Daemonizer, PIDFile
from configobj import ConfigObj
from validate import Validator

from webapp.dispatchers import Root, Fields, Summary, Detail


def _CORS():
    """Set HTTP Access Control Header to allow cross-site HTTP requests from
    any origin.
    """
    if cherrypy.request.method == 'OPTIONS':
        # http://www.html5rocks.com/en/tutorials/cors/
        # http://stackoverflow.com/questions/28049898/415-exception-cherrypy-webservice
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        cherrypy.response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        #cherrypy.response.headers['Access-Control-Allow-Headers'] = '*'
        #cherrypy.response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,OPTIONS,DELETE'
        cherrypy.response.headers['Access-Control-Allow-Methods'] = '*'
        return True
    else:
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'

def _term_handler(signal, frame):
    """Gracefully shutdown the server and exit.

    This function is intended to be registered as a SIGTERM handler.
    """
    logger = logging.getLogger('mtt')
    logger.info('Shutting down server')

    cherrypy.engine.exit()
    logger.info('Exiting')
    sys.exit(0)

def _restart_handler(signal, frame):
    """Restart the server.

    This function is intended to be registered as a SIGHUP handler.
    """
    logger = logging.getLogger('mtt')
    logger.info('Restarting server')
    # FIXME: This needs to reload the config, including attrs in the .ini file
    cherrypy.engine.restart()
    logger.debug('Blocking cherrypy engine')
    cherrypy.engine.block()

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Default conf. Some of these can/will be overrided by attrs in the .ini file
    conf = {
        'global': {
            'server.socket_host': socket.gethostbyname(socket.gethostname()),
            'log.access_file': '../log/access.log',
            'log.error_file': '../log/cherrypy_error.log',
            'log.screen': False,

            # Don't run CherryPy Checker on custom conf sections:
            # FIXME: This setting doesn't seem to be working...
            'checker.check_internal_config': False,
        },

        '/': {
            'tools.sessions.on': True,
            'tools.proxy.on': True,
            'tools.response_headers.on': True,
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.CORS.on': True
        },

        'internal': {
            'PIDfile': script_dir + '/.mttServer.pid',
            'log_level': 'INFO',
            'mtt_log_file': '../log/mtt.log'
        }
    }

    #
    # Load config.ini and integrate appropriate attrs into cherrpy conf.
    #
    ini = ConfigObj('../bin/mtt_server_config.ini',
                    configspec='mtt_server_config.spec')
    ini.validate(Validator())
    if 'server' in ini.keys():
        for k in ini['server']:
            conf['global']['server.' + k] = ini['server'][k]
    
    if 'logging' in ini.keys():
        if 'log_level' in ini['logging'].keys():
            conf['internal']['log_level'] = ini['logging']['log_level']
        if 'log_file' in ini['logging'].keys():
            log_file = ini['logging']['log_file']
            if not log_file.startswith('/'):
                # Path is relative to config.ini location
                log_file = '../' + ini['logging']['log_file']
            conf['internal']['mtt_log_file'] = log_file

    cherrypy.config.update(conf)

    #
    # Set up logging.
    #
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    logger = logging.getLogger('mtt')
    logger.setLevel(log_levels[conf['internal']['log_level']])
    handler = logging.FileHandler(conf['internal']['mtt_log_file'])
    handler.setFormatter(
        logging.Formatter('[%(asctime)s] %(levelname)s %(message)s'))
    logger.addHandler(handler)
    logger.info('Logging at %s to %s' % (conf['internal']['log_level'],
                                         conf['internal']['mtt_log_file']))

    # Log the PID
    PIDFile(cherrypy.engine, conf['internal']['PIDfile']).subscribe()

    #
    # Setup the service
    #
    Daemonizer(cherrypy.engine).subscribe()
    #cherrypy.tools.CORS = cherrypy.Tool('before_finalize', _CORS)
    #cherrypy.tools.CORS = cherrypy.Tool('before_handler', _CORS)
    cherrypy.tools.CORS = cherrypy._cptools.HandlerTool( _CORS )

    cherrypy.tree.mount(Root(ini),       '/',         conf)
    cherrypy.tree.mount(Fields(ini),     '/fields',   conf)
    cherrypy.tree.mount(Summary(ini),    '/summary',  conf)
    cherrypy.tree.mount(Detail(ini),     '/detail',   conf)

    logger.info('Starting cherrypy engine')
    cherrypy.engine.start()
    logger.debug('Registering signal handlers')
    signal.signal(signal.SIGTERM, _term_handler)
    signal.signal(signal.SIGHUP, _restart_handler)
    logger.debug('Blocking cherrypy engine')
    cherrypy.engine.block()
