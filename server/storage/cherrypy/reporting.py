import cherrypy

import os, os.path

import random
import string
import json

import datetime

import ConfigParser
import summary
import detail
import pprint

class _JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.timedelta):
            return str("abs")
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return super().default(obj)
    def iterencode(self, value):
        # Adapted from cherrypy/_cpcompat.py
        for chunk in super().iterencode(value):
            yield chunk.encode("utf-8")

json_encoder = _JSONEncoder()

def json_handler(*args, **kwargs):
    # Adapted from cherrypy/lib/jsontools.py
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
    return json_encoder.iterencode(value)
                                                                                            
class Reporting(object):
    config_file = None
    db_settings = {}
    
    def __init__(self, conffile=None):
        self.config_file=conffile
        config = ConfigParser.ConfigParser()
        config.read( conffile );

        # JJH do not hardcode the section
        section = "mttflat"
        for option in config.options( section ):
            try:
                self.db_settings[option] = config.get( section, option)
                if self.db_settings[option] == -1 :
                    DebugPrint("Skipping option: %s" % option)
            except:
                print("Exception on %s!" % option)
                self.db_settings[option] = None
        
        
    #
    # index: /
    #
    @cherrypy.expose
    def index(self):
        html = """<html>
           <head>
             <title>MTT Storage Welcome Page</title>
           </head>
           <body>
             <h2>Welcome ot the MTT Storage service welcome page!</h2>
             <p>
             If you know your party's extension enter the URL at any time.
             If not then consult the documentation.
             </p>
             <ul>
               <li>Server Fields: <a href=\"fields\">Click here</a>
               <li>Summary Views: <a href=\"summary\">Click here</a>
               <li>Detail Views: <a href=\"detail\">Click here</a>
               <li>
             </ul>
           </body>
           </html>"""
        return html

    #
    # summary: /fields
    #
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def fields(self, phase="all"):
        return summary.fields(self.db_settings, cherrypy.session);

    #
    # summary: /summary
    #
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def summary(self, phases="all"):
        data = {}
        start_time = datetime.datetime.now()
        end_time = datetime.datetime.now()

        print "m" * 80
        print "m" * 80
        print "m" * 80
        print "mmmm  New Summary Request"
        print "m" * 80

        print "----------------------"
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(cherrypy.request.headers)
        print "----------------------"

        print "-" * 70
        print "Preprocess parameters"

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
            print "Type: %s" %( type(data["phases"]) )
            print "(All) = " + json.dumps(data, sort_keys=True, indent=4, separators=(',',': '))
        # Otherwise build it from the parameters
        else:
            print "Not a JSON Request"
            data["phases"] = phases
            
        print "(Phase) = \""+ ",".join(phases) +"\""
        
        cherrypy.session['phases'] = phases

        #
        # Check settings for DB connection
        #
        print "-" * 70
        print "Check settings"
        rtn_msg = self.check_settings()
        if None != rtn_msg:
            rtn = { "fields" : None, "values" : None, "timing" : str(datetime.datetime.now() - start_time) }
            rtn['status'] = -1
            rtn['status_msg'] = "Server " + rtn_msg
            return rtn

        #
        # Validate the search parameters
        #
        print "-" * 70
        print "Validate Parameters"
        rtn = summary.validate_search_parameters(self.db_settings, cherrypy.session, data)
        if rtn['status'] != 0:
            print "Validate Failed:"
            print "Returned: " + str(rtn['status']) + ") " + rtn['status_msg']
            return rtn
        
        #
        # Perform the search
        #
        print "-" * 70
        print "Perform search"
        rtn = summary.index(self.db_settings, cherrypy.session, data)
        
        rtn['status'] = 0
        rtn['status_msg'] = 'Success'
        rtn['timing'] = str(datetime.datetime.now() - start_time)

        #print "(Final) " + json.dumps(rtn, sort_keys=True, indent=4, separators=(',',': '))
        
        return rtn;


    
    #
    # summary: /detail
    #     @cherrypy.tools.json_out(handler=json_handler)
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def detail(self, phases="all"):
        data = {}
        start_time = datetime.datetime.now()
        end_time = datetime.datetime.now()

        print "m" * 80
        print "m" * 80
        print "m" * 80
        print "mmmm  New Detail Request"
        print "m" * 80

        print "----------------------"
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(cherrypy.request.headers)
        print "----------------------"

        print "-" * 70
        print "Preprocess parameters"

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
            print "Type: %s" %( type(data["phases"]) )
            print "(All) = " + json.dumps(data, sort_keys=True, indent=4, separators=(',',': '))
        # Otherwise build it from the parameters
        else:
            print "Not a JSON Request"
            data["phases"] = phases
            
        print "(Phase) = \""+ ",".join(phases) +"\""
        
        cherrypy.session['phases'] = phases

        #
        # Check settings for DB connection
        #
        print "-" * 70
        print "Check settings"
        rtn_msg = self.check_settings()
        if None != rtn_msg:
            rtn = { "fields" : None, "values" : None, "timing" : str(datetime.datetime.now() - start_time) }
            rtn['status'] = -1
            rtn['status_msg'] = "Server " + rtn_msg
            return rtn

        #
        # Validate the search parameters
        #
        print "-" * 70
        print "Validate Parameters"
        rtn = summary.validate_search_parameters(self.db_settings, cherrypy.session, data, False)
        if rtn['status'] != 0:
            print "Validate Failed:"
            print "Returned: " + str(rtn['status']) + ") " + rtn['status_msg']
            return rtn
        
        #
        # Perform the search
        #
        print "-" * 70
        print "Perform search"
        rtn = detail.index(self.db_settings, cherrypy.session, data)

        #
        # Shape up the output header
        #
        rtn['status'] = 0
        rtn['status_msg'] = 'Success'
        rtn['timing'] = str(datetime.datetime.now() - start_time)

        #print "-" * 70
        #pp.pprint(rtn)
        #print "-" * 70
        
        return rtn;

    def check_settings(self):
        if None == self.db_settings.get("type") or None == self.db_settings["type"]:
            return "Error: Configuration settings missing the \"type\" field"
        if None == self.db_settings.get("dbname") or None == self.db_settings["dbname"]:
            return "Error: Configuration settings missing the \"dbname\" field"
        if None == self.db_settings.get("username") or None == self.db_settings["username"]:
            return "Error: Configuration settings missing the \"username\" field"
        if None == self.db_settings.get("password") or None == self.db_settings["password"]:
            return "Error: Configuration settings missing the \"password\" field"
        return None

def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    #cherrypy.response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    cherrypy.response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    #cherrypy.response.headers["Allow"] = "GET,POST,OPTIONS"
    
if __name__ == '__main__':
    cherrypy.tools.CORS = cherrypy.Tool('before_finalize', CORS)
    cherrypy.quickstart( Reporting("conf/mtt.conf"), '/', "conf/app.conf" )
