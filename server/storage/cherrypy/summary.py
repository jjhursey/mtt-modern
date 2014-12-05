#
# Summary reporting
#

import psycopg2
import string
import re

def fields(db_settings, session=[]):
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
            "suite_name"          : "Test Suite",
            "test_name"           : "Test",
            "compute_cluster"     : "Cluster",
            "compiler"            : "Compiler",
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
    return rtn


def index(db_settings, session=[], data=[]):
    rtn = ""
    json_rtn = ""
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
    print "SQL: " + sql
    cur.execute(sql +";")
    rows = cur.fetchall()

    json_rtn = { "fields" : fields, "values" : rows }

    #
    # Build the response
    #
    num = 1
    for row in rows:
        #rtn += "Row " + str(num) + ") " + row[0] + "\n"
        #json_rtn = row;
        rtn += str(row) + "\n\n"
        num += 1
    
    #
    # Close the connection
    #
    cur.close()
    conn.close()

    #
    #
    #
    #rtn = "Results: " + rtn
    #rtn = list(range(int(10)))
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
    
    where = """
           WHERE
              mpi_install.mpi_install_id > 0 """
    
    sql = None

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
    select_base_fields = ",\n\t".join(fields)
    select_base_out_fields = select_base_fields
    select_base_out_fields = re.sub(r'mpi_install.', 'results.', select_base_out_fields)
    select_base_out_fields = re.sub(r'test_build.', 'results.', select_base_out_fields)
    
    select_agg_out_fields = ""

    select_agg_sub_m_fields = ""
    select_agg_sub_b_fields = ""
    select_agg_sub_r_fields = ""

    select_agg_dummy_m_fields  = ""
    select_agg_dummy_m_fields += ",\n\t(0) as _mpi_p"
    select_agg_dummy_m_fields += ",\n\t(0) as _mpi_f"

    select_agg_dummy_b_fields  = ""
    select_agg_dummy_b_fields += ",\n\t(0) as _build_p"
    select_agg_dummy_b_fields += ",\n\t(0) as _build_f"

    select_agg_dummy_r_fields  = ""
    select_agg_dummy_r_fields += ",\n\t(0) as _run_p"
    select_agg_dummy_r_fields += ",\n\t(0) as _run_f"
    select_agg_dummy_r_fields += ",\n\t(0) as _run_s"
    select_agg_dummy_r_fields += ",\n\t(0) as _run_t"
    
    select_from_m = "\n"
    select_from_b = "\n"
    select_from_r = "\n"
    
    if 'install' in data['phases'] or 'all' in data['phases']:
        fields.append("mpi_install_pass")
        fields.append("mpi_install_fail")

        select_agg_out_fields += ",\n\tSUM(_mpi_p) as mpi_install_pass"
        select_agg_out_fields += ",\n\tSUM(_mpi_f) as mpi_install_fail"

        select_agg_sub_m_fields += ",\n\t(CASE WHEN mpi_install.test_result = 1 THEN 1 ELSE 0 END) as _mpi_p"
        select_agg_sub_m_fields += ",\n\t(CASE WHEN mpi_install.test_result = 0 THEN 1 ELSE 0 END) as _mpi_f"

        select_from_m += "\n\t mpi_install"
    if 'test_build' in data['phases'] or 'all' in data['phases']:
        fields.append("test_build_pass")
        fields.append("test_build_fail")

        select_agg_out_fields += ",\n\tSUM(_build_p) as test_build_pass"
        select_agg_out_fields += ",\n\tSUM(_build_f) as test_build_fail"

        select_agg_sub_b_fields += ",\n\t(CASE WHEN test_build.test_result = 1 THEN 1 ELSE 0 END) as _build_p"
        select_agg_sub_b_fields += ",\n\t(CASE WHEN test_build.test_result = 0 THEN 1 ELSE 0 END) as _build_f"

        select_from_b += "\n\t test_build"
    if 'test_run' in data['phases'] or 'all' in data['phases']:
        fields.append("test_run_pass")
        fields.append("test_run_fail")
        fields.append("test_run_skip")
        fields.append("test_run_timed")

        select_agg_out_fields += ",\n\tSUM(_run_p) as test_run_pass"
        select_agg_out_fields += ",\n\tSUM(_run_f) as test_run_fail"
        select_agg_out_fields += ",\n\tSUM(_run_s) as test_run_skip"
        select_agg_out_fields += ",\n\tSUM(_run_t) as test_run_timed"

        select_agg_sub_r_fields += ",\n\t(CASE WHEN test_run.test_result = 1 THEN 1 ELSE 0 END) as _run_p"
        select_agg_sub_r_fields += ",\n\t(CASE WHEN test_run.test_result = 0 THEN 1 ELSE 0 END) as _run_f"
        select_agg_sub_r_fields += ",\n\t(CASE WHEN test_run.test_result = 2 THEN 1 ELSE 0 END) as _run_s"
        select_agg_sub_r_fields += ",\n\t(CASE WHEN test_run.test_result = 3 THEN 1 ELSE 0 END) as _run_t"

        select_from_r += "\n\t test_run"
        
    print "SF: " + select_base_fields


    #
    # Build Basic SQL
    #
    if need_table("submit", tablesd) == True:
        select_from_m += "\n\t\t JOIN submit using (submit_id)"
        select_from_b += "\n\t\t JOIN submit using (submit_id)"
        select_from_r += "\n\t\t JOIN submit using (submit_id)"
    if need_table("mpi_install", tablesd) == True:
        select_from_b += "\n\t\t JOIN mpi_install using (mpi_install_id)"
        select_from_r += "\n\t\t JOIN mpi_install using (mpi_install_id)"
        
    sql  = "SELECT \n\t" + select_base_out_fields
    sql += select_agg_out_fields
    sql += "\n\tFROM ("

    #
    # All phases - Union the three tables of data
    #
    if 'all' in data['phases'] or len(data['phases']) == 3:
        sql += "\n("
        
        sql += "\n\t\tSELECT \n\t" + select_base_fields
        sql += select_agg_sub_m_fields
        sql += select_agg_dummy_b_fields
        sql += select_agg_dummy_r_fields
        sql += "\n\tFROM " + select_from_m
        sql += where
        qualify = "mpi_install."
        if "start_timestamp" in data['search']:
            sql += "\n\t AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"
        if "end_timestamp" in data['search']:
            sql += "\n\t AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"
        

        sql += "\n) UNION ALL ("

        
        sql += "\n\t\tSELECT \n\t" + select_base_fields
        sql += select_agg_dummy_m_fields
        sql += select_agg_sub_b_fields
        sql += select_agg_dummy_r_fields
        sql += "\n\tFROM " + select_from_b
        sql += where
        qualify = "test_build."
        if "start_timestamp" in data['search']:
            sql += "\n\t AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"
        if "end_timestamp" in data['search']:
            sql += "\n\t AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"

            
        sql += "\n) UNION ALL ("

        
        sql += "\n\t\tSELECT \n\t" + select_base_fields
        sql += select_agg_dummy_m_fields
        sql += select_agg_dummy_b_fields
        sql += select_agg_sub_r_fields
        sql += "\n\tFROM " + select_from_r
        sql += where
        qualify = "test_run."
        if "start_timestamp" in data['search']:
            sql += "\n\t AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"
        if "end_timestamp" in data['search']:
            sql += "\n\t AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"

        sql += "\n)"
    #
    # MPI Install
    #
    elif 'install' in data['phases'] and len(data['phases']) == 1:
        qualify = "mpi_install."
        if "start_timestamp" in data['search']:
            where += "\n\t AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"

        if "end_timestamp" in data['search']:
            where += "\n\t AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"

        sql += "\n\t\tSELECT \n\t" + select_base_fields + select_agg_sub_m_fields
        sql += "\n\tFROM " + select_from_m
        sql += where
    #
    # Test Build
    #
    elif 'test_build' in data['phases'] and len(data['phases']) == 1: 
        qualify = "test_build."
        if "start_timestamp" in data['search']:
            where += "\n\t AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"

        if "end_timestamp" in data['search']:
            where += "\n\t AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"

        sql += "\n\t\tSELECT \n\t" + select_base_fields + select_agg_sub_b_fields
        sql += "\n\tFROM " + select_from_b
        sql += where
    #
    # Test Run
    #
    elif 'test_run' in data['phases'] and len(data['phases']) == 1:
        qualify = "test_run."
        if "start_timestamp" in data['search']:
            where += "\n\t AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"

        if "end_timestamp" in data['search']:
            where += "\n\t AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"

        sql += "\n\t\tSELECT \n\t" + select_base_fields + select_agg_sub_r_fields
        sql += "\n\tFROM " + select_from_r
        sql += where
    #
    # MPI Install, Test Build
    #
    elif 'install' in data['phases'] and 'test_build' in data['phases'] and len(data['phases']) == 2:
        return None
    #
    # Test Build, Test Run
    #
    elif 'test_build' in data['phases'] and 'test_run' in data['phases'] and len(data['phases']) == 2:
        return None
    #
    # MPI Install, Test Run
    #
    elif 'install' in data['phases'] and 'test_run' in data['phases'] and len(data['phases']) == 2:
        return None

    
    #
    # Return SQL
    #
    sql += ") as results"

    
    sql += "\n\tGROUP BY \n\t" + select_base_out_fields
    sql += "\n\tORDER BY \n\t" + select_base_out_fields
    sql += "\n\tOFFSET 0"

    return sql, fields
