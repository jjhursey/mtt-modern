import cherrypy

import os, os.path

import random
import string

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
               <li>Summary Data: <a href=\"summary\">Click here</a>
             </ul>
           </body>
           </html>"""
        return html

    #
    # summary: /fields
    #
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def fields(self,phase="all"):
        return summary.fields(self.db_settings, cherrypy.session);

    #
    # summary: /summary
    #
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def summary(self,phase="all"):
        cherrypy.session['phase'] = phase

        rtn = self.check_settings()
        if None != rtn:
            return rtn
        
        rtn = summary.index(self.db_settings, cherrypy.session);
        
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
