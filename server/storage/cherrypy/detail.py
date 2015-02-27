#
# Summary reporting
#

import psycopg2
import string
import re
import pprint

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
    sql, fields = build_sql(session, data)
    if None == sql:
        return { "fields" : fields, "values" : None }
    print "SQL:\n " + sql
    cur.execute(sql +";")
    rows = cur.fetchall()

    json_rtn = { "fields" : fields, "values" : rows }

    #
    # Build the response
    #
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

#################################################################
# The SQL Table structure helps us determine which tables are
# needed to access the necessary fields that the user requested.
#################################################################
def get_sql_table_structure():
    rtn = { "submit": [
               "hostname",
               "local_username",
               "http_username",
               "mtt_client_version"
               ],
            "results_fields": [
               "description",
               "start_timestamp",
               "submit_timestamp",
               "duration",
               "trial",
               "test_result",
               "environment",
               "result_stdout",
               "result_stderr",
               "result_message",
               "merge_stdout_stderr",
               "exit_value",
               "exit_signal"
               ],
            "mpi_install": [
               "platform_name",
               "platform_hardware",
               "platform_type",
               "os_name",
               "os_version",
               "mpi_name",
               "mpi_version",
               "compiler_name",
               "compiler_version",
               "vpath_mode",
               "bitness",
               "endian",
               "configure_arguments"
               ],
            "test_build": [
               "compiler_name",
               "compiler_version",
               "test_suite_name",
               "test_suite_description"
               ],
            "test_run": [
               "test_name",
               "test_name_description",
               "launcher",
               "resource_mgr",
               "parameters",
               "network",
               "np",
               "full_command"
               ]
         };
    return rtn;


def preprocess_phase(phases):
    true_phase = None
    
    for phase in phases:
        if 'install' == phase:
            true_phase = "mpi_install"
        elif 'test_build' == phase:
            true_phase = "test_build"
        elif 'test_run' == phase:
            true_phase = "test_run"
        elif 'all' == phase:
            true_phase = "all"
        else:
            true_phase = phase
            return (-1, true_phase)

    return (0, true_phase)

def which_table_contains(field):
    tables = []
    sql_tables = get_sql_table_structure()

    for t in sql_tables:
        for f in sql_tables[t]:
            if field == f:
                tables.append(t)

    return tables

def preprocess_field(field):
    if field == "start_timestamp":
        return "start_timestamp"
    elif field == "end_timestamp":
        return "start_timestamp"
    else:
        return field

def need_table(table_name, all_cols):
    for field,table in all_cols.iteritems():
        if table_name == table:
            return True
    return False

def build_sql(session=[], data=[]):
    fields = []
    tables = []
    tablesd = {}
    with_duration = False
    
    where = "\n\t" + "mpi_install.mpi_install_id > 0 "
    
    sql = None

    #data['columns'].append("test_result")
    #data['columns'].append("http_username")
    #data['columns'].append("mpi_install_id")
    #data['columns'].append("duration")
    #data['columns'].append("result_message")
    #data['columns'].append("result_stdout")
    #data['columns'].append("result_stderr")

    if "duration" in data['columns']:
        data['columns'].remove("duration")
        with_duration = True

        
    #################################################################
    # Columns required
    #################################################################
    sql_tables = get_sql_table_structure()
    
    #
    # For each of the columns requested, determine which table(s) we need
    #
    print "Columns:"
    for col in data['columns']:
        col = preprocess_field(col)
        
        tables = which_table_contains(col)
        if 0 == len(tables):
            print "Error: Cound not find the field (%s). Skipping!" % (col)
        elif 1 == len(tables):
            print "\t%20s\tTable: %s" %(col, tables[0])
            if col not in tablesd:
                tablesd[col] = tables[0]
        else:
            if 'install' in data['phases'] and 'mpi_install' in tables:
                col = "mpi_install."+col
                tablesd[col] = "mpi_install"
            elif 'test_build' in data['phases'] and 'test_build' in tables:
                col = "test_build."+col
                tablesd[col] = "test_build"
            elif 'test_run' in data['phases'] and 'test_run' in tables:
                col = "test_run."+col
                tablesd[col] = "test_run"
            elif 'all' in data['phases']:
                col = "mpi_install."+col
                tablesd[col] = "mpi_install"
            else:
                print "Multiple matches for (%s). In tables %s" %(col, ", ".join(tables))

        fields.append(col)
        

    #
    # For each of the search parameters requested, determine which table(s) we need
    #
    print "Search:"
    for col in data['search']:
        col = preprocess_field(col)
        
        tables = which_table_contains(col)
        if 0 == len(tables):
            print "Error: Cound not find the field (%s). Skipping!" % (col)
        elif 1 == len(tables):
            print "\t%20s\tTable: %s" %(col, tables[0])
            if col not in tablesd:
                tablesd[col] = tables[0]
        else:
            if 'install' in data['phases'] and 'mpi_install' in tables:
                tablesd[col] = "mpi_install"
            elif 'test_build' in data['phases'] and 'test_build' in tables:
                tablesd[col] = "test_build"
            elif 'test_run' in data['phases'] and 'test_run' in tables:
                tablesd[col] = "test_run"
            print "Multiple matches for (%s). In tables %s" %(col, ", ".join(tables))

            
    #
    # Debug Display the fields and the required tables
    #
    print "-"*40
    for f in fields:
        print "FIELDS : " + f
    print "-"*40
    for k,v in tablesd.iteritems():
        print "REQUIRE: %20s in %s" % (k,v)
    print "-"*40

    
    #################################################################
    # Search Parameters
    #################################################################
    qualify = ""
    if 'install' in data['phases']:
        qualify = "mpi_install."
    elif 'test_build' in data['phases']:
        qualify = "test_build."
    elif 'test_run' in data['phases']:
        qualify = "test_run."
    else:
        qualify = ""

    #
    # Process data range - Done below per case to avoid conflicts
    #

    #
    # Process Platform information
    #
    if "platform_name" in data['search']:
        where += "\n\t AND platform_name = '"+data['search']['platform_name']+"'"

    if "platform_hardware" in data['search']:
        where += "\n\t AND platform_hardware = '"+data['search']['platform_hardware']+"'"

    if "os_name" in data['search']:
        where += "\n\t AND os_name = '"+data['search']['os_name']+"'"


    #
    # Process MPI Information
    #
    if "mpi_version" in data['search']:
        where += "\n\t AND mpi_version = '"+data['search']['mpi_version']+"'"
    if "mpi_name" in data['search']:
        where += "\n\t AND mpi_name = '"+data['search']['mpi_name']+"'"

    #
    # Process Compiler
    #
    if "compiler_name" in data['search']:
        if 'install' in data['phases']:
            qualify = "mpi_install."
        elif 'test_build' in data['phases']:
            qualify = "test_build."
        else:
            qualify = "mpi_install."
        where += "\n\t AND "+qualify+"compiler_name = '"+data['search']['compiler_name']+"'"
        

    #################################################################
    # Phases
    #################################################################
    select_from_table = ""
    select_from_other_table = ""

    #
    # Required 
    #
    #fields.append("test_result")
    #fields.append("result_message")
    #fields.append("result_stdout")
    #fields.append("result_stderr")

    #
    #
    #
    if 'install' in data['phases']:
        select_from_table = "mpi_install"
    elif 'test_build' in data['phases']:
        select_from_table = "test_build"
    elif 'test_run' in data['phases']:
        select_from_table = "test_run"
    else:
        return None

    qualify = select_from_table + "."
    select_from_table = "\n\t" + select_from_table

    #
    # Add qualifier to all common "results_fields"
    #
    tbl_str = get_sql_table_structure()
    for tblf in tbl_str["results_fields"]:
        bv = False
        for fld in fields:
            if tblf == fld:
                bv = True
        if bv == True:
            fields.remove(tblf)
            fields.append(qualify + tblf)

    select_base_fields  = ",\n\t".join(fields)
    
    select_base_out_fields = select_base_fields
    select_base_out_fields = re.sub(r'mpi_install.', 'results.', select_base_out_fields)
    select_base_out_fields = re.sub(r'test_build.', 'results.', select_base_out_fields)
    
        
    print "SF: " + select_base_fields


    #
    # Build Basic SQL
    #
    if need_table("submit", tablesd) == True:
        select_from_other_table += "\n\t JOIN submit using (submit_id)"
    if need_table("mpi_install", tablesd) == True and not 'install' in data['phases']:
        select_from_other_table += "\n\t JOIN mpi_install using (mpi_install_id)"
        
    sql  = "SELECT \n\t" + select_base_fields
    if with_duration == True:
        sql += ",\n\tto_char("+qualify+"duration, 'HH24:MI:SS') as duration"
    sql += "\n"
    sql += " FROM " + select_from_table + select_from_other_table

    if "start_timestamp" in data['search']:
        where += "\n\t" + "AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"

    if "end_timestamp" in data['search']:
        where += "\n\t" + "AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"

    sql += "\n"
    sql += " WHERE " + where

    #
    # Return SQL
    #
    #sql += "\n" + " GROUP BY \n\t" + select_base_out_fields
    #sql += "\n" + " ORDER BY \n\t" + select_base_out_fields
    sql += "\n" + " OFFSET 0"
    #sql += "\n" + " LIMIT 2"

    final_fields = []
    for f in fields:
        if re.match(qualify, f):
            final_fields.append(re.sub(qualify, '', f))
        else:
            final_fields.append(f)
            
    if with_duration == True:
        fields.append("duration")
        final_fields.append("duration")
    
    return sql, final_fields
