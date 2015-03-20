#
# Summary reporting
#

import psycopg2
import string
import re
import pprint

import data_pg_flat

'''
SELECT
http_username,
platform_name,
platform_hardware,
os_name,
mpi_name,
mpi_version,
compiler_version,
configure_arguments,
description,
exit_value,
exit_signal,
result_message,
result_stdout,
result_stderr,
environment
compiler_name,
vpath_mode,

bitness,
endian,
duration,
client_serial,
'''

def index(db_settings, session=[], data=[]):
    rtn = ""
    json_rtn = ""
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


    
    #
    # Open the database connection
    #
    conn = psycopg2.connect("dbname="+db_settings["dbname"]+
                            " user="+db_settings["username"]+
                            " password="+db_settings["password"]+
                            " host="+db_settings["server"]+
                            " port="+db_settings["port"])
    cur = conn.cursor()

    #
    # Find the necessary values
    #
    sql, fields = data_pg_flat.build_detail_sql(session, data)
    if None == sql:
        return { "fields" : fields, "values" : None }
    print "SQL:\n " + sql
    cur.execute(sql +";")
    rows = cur.fetchall()

    json_rtn = { "fields" : fields, "values" : rows }

    #
    # Build the response
    #
    print "Returning: " + str(len(rows)) + " values (rows)"
    #print "-*" * 40
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(rows)
    #print "-*" * 40

    #
    # Close the connection
    #
    cur.close()
    conn.close()

    #
    #
    #
    return json_rtn
