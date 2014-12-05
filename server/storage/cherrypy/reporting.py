import cherrypy

import os, os.path

import random
import string
import json

import ConfigParser
import summary

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
               <li>
               <table border="1">
                 <tr>
                   <th><a href=\"summary\">All Phases</a></th>
                   <th>Install</th>
                   <th>Test Build</th>
                   <th>Test Run</th>
                 </tr>
                 <tr>
                   <td>Install</td>
                   <td><a href=\"summary?phase=install\">Click</a></td>
                   <td><a href=\"summary?phase=install,test_build\">Click</a></td>
                   <td><a href=\"summary?phase=install,test_run\">Click</a></td>
                 </tr>
                 <tr>
                   <td>Test Build</td>
                   <td></td>
                   <td><a href=\"summary?phase=test_build\">Click</a></td>
                   <td><a href=\"summary?phase=test_build,test_run\">Click</a></td>
                 </tr>
                 <tr>
                   <td>Test Run</td>
                   <td></td>
                   <td></td>
                   <td><a href=\"summary?phase=test_run\">Click</a></td>
                 </tr>
               </table>
               <li>Summary Data: <a href=\"summary\">Click here</a>
               <li>Summary Data (install): <a href=\"summary?phase=install\">Click here</a>
               <li>Summary Data (test_build): <a href=\"summary?phase=test_build\">Click here</a>
               <li>Summary Data (test_run): <a href=\"summary?phase=test_run\">Click here</a>
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
        
        # If they sent JSON data, then use that
        if hasattr(cherrypy.request, "json"):
            data = cherrypy.request.json
            phases = data["phases"]
            print "DEBUG: " + json.dumps(data, sort_keys=True, indent=4, separators=(',',': '))
        # Otherwise build it from the parameters
        else:
            data["phases"] = phases
            
        print "DEBUG: (Phase) = \""+ ",".join(phases) +"\""

        cherrypy.session['phases'] = phases

        rtn = self.check_settings()
        if None != rtn:
            return rtn
        
        rtn = summary.index(self.db_settings, cherrypy.session, data);
        
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

if __name__ == '__main__':
    cherrypy.quickstart( Reporting("conf/mtt.conf"), '/', "conf/app.conf" )
