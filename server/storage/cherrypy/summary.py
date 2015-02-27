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


def validate_search_parameters(db_settings, session=[], data=[], is_summary=True):
    rtn = { "fields" : None, "values" : None }

    #
    # Make sure that only the three fields are specified
    #
    if len(data) != 3:
        rtn['status'] = -2
        rtn['status_msg'] = "Validate Error: Expected exactly 3 fields. %d supplied." % (len(data))
        return rtn

    
    #
    # Check the 'phases' field
    #
    if 'phases' not in data:
        rtn['status'] = -3
        rtn['status_msg'] = "Validate Error: No 'phases' parameter specified."
        return rtn

    val, phase = preprocess_phase(data['phases'], is_summary)
    if phase == None or val != 0:
        rtn['status'] = -4
        rtn['status_msg'] = "Validate Error: Invalid 'phases' parameter: '%s'." % (phase)
        return rtn

    
    #
    # Check 'columns' field
    #
    if 'columns' not in data:
        rtn['status'] = -5
        rtn['status_msg'] = "Validate Error: No 'columns' parameter specified."
        return rtn
    
    if len(data['columns']) == 0:
        rtn['status'] = -6
        rtn['status_msg'] = "Validate Error: No values specified in the 'columns' parameter."
        return rtn
    
    for col in data['columns']:
        tables = which_table_contains(col)
        if len(tables) == 0:
            rtn['status'] = -7
            rtn['status_msg'] = "Validate Error: Invalid 'columns' parameter: '%s'." % ( col )
            return rtn

        
    #
    # Check 'search' field
    #
    if 'search' not in data:
        rtn['status'] = -8
        rtn['status_msg'] = "Validate Error: No 'search' parameter specified."
        return rtn
    
    if len(data['search']) == 0:
        rtn['status'] = -9
        rtn['status_msg'] = "Validate Error: No values specified in the 'search' parameter."
        return rtn

    has_start = False
    has_end   = False
    
    for col in data['search']:
        orig = col
        col = preprocess_field(col)
        tables = which_table_contains(col)
        if len(tables) == 0 and is_special_key(col) == False:
            rtn['status'] = -10
            rtn['status_msg'] = "Validate Error: Invalid 'search' parameter: '%s' = '%s'." % ( col, data['search'][col] )
            return rtn

        if orig == "start_timestamp":
            has_start = True

        if orig == "end_timestamp":
            has_end = True
            
        if col == "start_timestamp":
            if None == re.match("\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}", (data['search'][orig]) ):
                rtn['status'] = -11
                rtn['status_msg'] = "Validate Error: The 'search' parameter '%s' is not formatted correctly. Submission '%s' must be formatted as YYYY-MM-DD HH:MM:SS" % ( orig, data['search'][orig] )
                return rtn

    if has_start == False:
        rtn['status'] = -12
        rtn['status_msg'] = "Validate Error: The 'search' parameter 'start_timestamp' was not specified"
        return rtn

    if has_end == False:
        rtn['status'] = -13
        rtn['status_msg'] = "Validate Error: The 'search' parameter 'end_timestamp' was not specified"
        return rtn

    #
    # If we get there then we are ok
    #
    rtn['status'] = 0
    rtn['status_msg'] = "Success"

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
    print "SQL: \n" + sql
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
               "mpi_install_id",
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
               "test_build_id",
               "compiler_name",
               "compiler_version",
               "test_suite_name",
               "test_suite_description"
               ],
            "test_run": [
               "test_run_id",
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


def preprocess_phase(phases, is_summary=True):
    true_phase = None
    
    for phase in phases:
        if 'install' == phase:
            true_phase = "mpi_install"
        elif 'test_build' == phase:
            true_phase = "test_build"
        elif 'test_run' == phase:
            true_phase = "test_run"
        elif 'all' == phase and is_summary == True:
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

def get_keys_test_result():
    return [ "mpi_install_pass",
              "mpi_install_fail",
              "test_build_pass",
              "test_build_fail",
              "test_run_pass",
              "test_run_fail",
              "test_run_skip",
              "test_run_timed"]
#              "test_run_perf"]

def is_special_key(field):
    return field in get_keys_test_result()

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

def sql_create_outer_select_field(field, qualify=""):
    if field == "bitness":
        return """(CASE
          WHEN (bitness = B'000000')  THEN 'unknown'
          WHEN (bitness = B'000001')  THEN '8'
          WHEN (bitness = B'000010')  THEN '16'
          WHEN (bitness = B'000100')  THEN '32'
          WHEN (bitness = B'001000')  THEN '64'
          WHEN (bitness = B'001100')  THEN '32/64'
          WHEN (bitness = B'010000')  THEN '128'
          ELSE 'unknown' END) as bitness
        """
    elif field == "endian":
        return """(CASE
          WHEN (endian = B'01')       THEN 'little'
          WHEN (endian = B'10')       THEN 'big'
          ELSE 'unknown' END) as endian
        """
    elif field == "vpath_mode":
        return """(CASE
          WHEN (vpath_mode = B'01')       THEN 'relative'
          WHEN (vpath_mode = B'10')       THEN 'absolute'
          ELSE 'unknown' END) as vpath_mode
        """
    elif field == "duration":
        return "to_char("+qualify+"duration, 'HH24:MI:SS') as duration"
    else:
        return field

def build_sql(session=[], data=[]):
    fields = []
    tables = []
    tablesd = {}
    keys = {}
    
    where = "mpi_install.mpi_install_id > 0 "
    
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
            if is_special_key(col) == True:
                keys[col] = data['search'][col]
            else:
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
    for k,v in keys.iteritems():
        print "KEY: %20s matching '%s'" % (k,v)
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
        

    #
    # Special Key: pass/fail/skip/timed/perf
    #
    outer_where = ""
    keys_test_result = get_keys_test_result()
    for k in keys:
        if k in keys_test_result:
            outer_where += "\n\t"
            if outer_where != "\n\t":
                outer_where += " AND"

            if "mpi_install_pass" == k:
                outer_where += " _mpi_p "
            elif "mpi_install_fail" == k:
                outer_where += " _mpi_f "
            elif "test_build_pass" == k:
                outer_where += " _build_p "
            elif "test_build_fail" == k:
                outer_where += " _build_f "
            elif "test_run_pass" == k:
                outer_where += " _run_p "
            elif "test_run_fail" == k:
                outer_where += " _run_f "
            elif "test_run_skip" == k:
                outer_where += " _run_s "
            elif "test_run_timed" == k:
                outer_where += " _run_t "
            elif "test_run_perf" == k:
                outer_where += " _run_p "
    
            if keys[k] > 0:
                outer_where += "> 0"
            else:
                outer_where += " <= 0"

    #################################################################
    # Phases
    #################################################################
    group_by_fields = ""
    order_by_fields = ""
    select_inner_fields = ""
    
    #
    # Outer Select: Primary fields
    #
    countF = 0
    select_base_fields = ""
    qf = ""
    tbl_str = get_sql_table_structure()
    for f in fields:
        if f in tbl_str["results_fields"]:
            if qualify == "":
                qf = "mpi_install."
            else:
                qf = qualify
        else:
            qf = ""

        if countF == 0:
            select_base_fields  += "\n\t" + sql_create_outer_select_field(f, qf)
            group_by_fields     += "\n\t" + f
            order_by_fields     += "\n\t" + f
            select_inner_fields += "\n\t" + qf + f
        else:
            select_base_fields  += ",\n\t" + sql_create_outer_select_field(f, qf)
            group_by_fields     += ",\n\t" + f
            order_by_fields     += ",\n\t" + f
            select_inner_fields += ",\n\t" + qf + f

        countF += 1
        
    select_base_out_fields = select_base_fields
    select_base_out_fields = re.sub(r'mpi_install.', 'results.', select_base_out_fields)
    select_base_out_fields = re.sub(r'test_build.', 'results.', select_base_out_fields)
    select_base_out_fields = re.sub(r'test_run.', 'results.', select_base_out_fields)
    group_by_fields = re.sub(r'mpi_install.', 'results.', group_by_fields)
    group_by_fields = re.sub(r'test_build.', 'results.', group_by_fields)
    order_by_fields = re.sub(r'mpi_install.', 'results.', order_by_fields)
    order_by_fields = re.sub(r'test_build.', 'results.', order_by_fields)


    #
    # Outer Select: aggregation fields
    #
    select_agg_out_fields = ""

    if 'install' in data['phases'] or 'all' in data['phases']:
        fields.append("mpi_install_pass")
        fields.append("mpi_install_fail")

        select_agg_out_fields += ",\n\tSUM(_mpi_p) as mpi_install_pass"
        select_agg_out_fields += ",\n\tSUM(_mpi_f) as mpi_install_fail"

    if 'test_build' in data['phases'] or 'all' in data['phases']:
        fields.append("test_build_pass")
        fields.append("test_build_fail")

        select_agg_out_fields += ",\n\tSUM(_build_p) as test_build_pass"
        select_agg_out_fields += ",\n\tSUM(_build_f) as test_build_fail"

    if 'test_run' in data['phases'] or 'all' in data['phases']:
        fields.append("test_run_pass")
        fields.append("test_run_fail")
        fields.append("test_run_skip")
        fields.append("test_run_timed")

        select_agg_out_fields += ",\n\tSUM(_run_p) as test_run_pass"
        select_agg_out_fields += ",\n\tSUM(_run_f) as test_run_fail"
        select_agg_out_fields += ",\n\tSUM(_run_s) as test_run_skip"
        select_agg_out_fields += ",\n\tSUM(_run_t) as test_run_timed"

    #
    # Outer Select: Build it
    #
    sql  = "SELECT "
    sql += select_base_out_fields
    sql += select_agg_out_fields

        

    #
    # Inner Select: define aggregation fields and dummy versions
    #
    select_agg_sub_m_fields    = ""
    select_agg_sub_m_fields   += ",\n\t(CASE WHEN mpi_install.test_result = 1 THEN 1 ELSE 0 END) as _mpi_p"
    select_agg_sub_m_fields   += ",\n\t(CASE WHEN mpi_install.test_result = 0 THEN 1 ELSE 0 END) as _mpi_f"
    select_agg_dummy_m_fields  = ""
    select_agg_dummy_m_fields += ",\n\t(0) as _mpi_p"
    select_agg_dummy_m_fields += ",\n\t(0) as _mpi_f"

    select_agg_sub_b_fields    = ""
    select_agg_sub_b_fields   += ",\n\t(CASE WHEN test_build.test_result = 1 THEN 1 ELSE 0 END) as _build_p"
    select_agg_sub_b_fields   += ",\n\t(CASE WHEN test_build.test_result = 0 THEN 1 ELSE 0 END) as _build_f"
    select_agg_dummy_b_fields  = ""
    select_agg_dummy_b_fields += ",\n\t(0) as _build_p"
    select_agg_dummy_b_fields += ",\n\t(0) as _build_f"

    select_agg_sub_r_fields = ""
    select_agg_sub_r_fields += ",\n\t(CASE WHEN test_run.test_result = 1 THEN 1 ELSE 0 END) as _run_p"
    select_agg_sub_r_fields += ",\n\t(CASE WHEN test_run.test_result = 0 THEN 1 ELSE 0 END) as _run_f"
    select_agg_sub_r_fields += ",\n\t(CASE WHEN test_run.test_result = 2 THEN 1 ELSE 0 END) as _run_s"
    select_agg_sub_r_fields += ",\n\t(CASE WHEN test_run.test_result = 3 THEN 1 ELSE 0 END) as _run_t"
    select_agg_dummy_r_fields  = ""
    select_agg_dummy_r_fields += ",\n\t(0) as _run_p"
    select_agg_dummy_r_fields += ",\n\t(0) as _run_f"
    select_agg_dummy_r_fields += ",\n\t(0) as _run_s"
    select_agg_dummy_r_fields += ",\n\t(0) as _run_t"

        
    #
    # From tables
    #
    select_from_m = "\n\t mpi_install"
    select_from_b = "\n\t test_build"
    select_from_r = "\n\t test_run"
    if need_table("submit", tablesd) == True:
        select_from_m += "\n\t\t JOIN submit using (submit_id)"
        select_from_b += "\n\t\t JOIN submit using (submit_id)"
        select_from_r += "\n\t\t JOIN submit using (submit_id)"
    if need_table("mpi_install", tablesd) == True:
        select_from_b += "\n\t\t JOIN mpi_install using (mpi_install_id)"
        select_from_r += "\n\t\t JOIN mpi_install using (mpi_install_id)"
        
    #
    # Build Basic SQL
    #
        
    sql += "\nFROM ("

    #
    # All phases - Union the three tables of data
    #
    if 'all' in data['phases'] or len(data['phases']) == 3:
        sql += "\n("

        #
        # MPI Install
        #
        sql += "\n\t\tSELECT \n\t"
        sql += select_inner_fields
        sql += select_agg_sub_m_fields
        sql += select_agg_dummy_b_fields
        sql += select_agg_dummy_r_fields
        sql += "\n\tFROM " + select_from_m
        sql += "\n\tWHERE " + where
        qualify = "mpi_install."
        if "start_timestamp" in data['search']:
            sql += "\n\t AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"
        if "end_timestamp" in data['search']:
            sql += "\n\t AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"
        
        ###############
        sql += "\n) UNION ALL ("
        ###############
        
        #
        # Test Build
        #
        sql += "\n\t\tSELECT \n\t"
        sql += select_inner_fields
        sql += select_agg_dummy_m_fields
        sql += select_agg_sub_b_fields
        sql += select_agg_dummy_r_fields
        sql += "\n\tFROM " + select_from_b
        sql += "\n\tWHERE " + where
        qualify = "test_build."
        if "start_timestamp" in data['search']:
            sql += "\n\t AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"
        if "end_timestamp" in data['search']:
            sql += "\n\t AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"

        ###############
        sql += "\n) UNION ALL ("
        ###############
        
        #
        # Test Run
        #
        sql += "\n\t\tSELECT \n\t"
        sql += select_inner_fields
        sql += select_agg_dummy_m_fields
        sql += select_agg_dummy_b_fields
        sql += select_agg_sub_r_fields
        sql += "\n\tFROM " + select_from_r
        sql += "\n\tWHERE " + where
        qualify = "test_run."
        if "start_timestamp" in data['search']:
            sql += "\n\t AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"
        if "end_timestamp" in data['search']:
            sql += "\n\t AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"

        ###############
        sql += "\n)"
        ###############
    #
    # MPI Install
    #
    elif 'install' in data['phases'] and len(data['phases']) == 1:
        qualify = "mpi_install."
        if "start_timestamp" in data['search']:
            where += "\n\t AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"

        if "end_timestamp" in data['search']:
            where += "\n\t AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"

        sql += "\n\tSELECT "
        sql += select_inner_fields
        sql += select_agg_sub_m_fields

        sql += "\n\tFROM " + select_from_m
        sql += "\n\tWHERE " + where
    #
    # Test Build
    #
    elif 'test_build' in data['phases'] and len(data['phases']) == 1: 
        qualify = "test_build."
        if "start_timestamp" in data['search']:
            where += "\n\t AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"

        if "end_timestamp" in data['search']:
            where += "\n\t AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"

        sql += "\n\tSELECT "
        sql += select_inner_fields
        sql += select_agg_sub_b_fields

        sql += "\n\tFROM " + select_from_b
        sql += "\n\tWHERE " + where
    #
    # Test Run
    #
    elif 'test_run' in data['phases'] and len(data['phases']) == 1:
        qualify = "test_run."
        if "start_timestamp" in data['search']:
            where += "\n\t AND "+qualify+"start_timestamp >= '"+data['search']['start_timestamp']+"'"

        if "end_timestamp" in data['search']:
            where += "\n\t AND "+qualify+"start_timestamp <= '"+data['search']['end_timestamp']+"'"

        sql += "\n\tSELECT "
        sql += select_inner_fields
        sql += select_agg_sub_r_fields

        sql += "\n\tFROM " + select_from_r
        sql += "\n\tWHERE " + where
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
    sql += "\n     ) as results"

    if outer_where != "":
        sql += "\nWHERE " + outer_where
        
    sql += "\nGROUP BY " + group_by_fields
    sql += "\nORDER BY " + order_by_fields
    sql += "\nOFFSET 0"

    final_fields = []
    for f in fields:
        if re.match(r'mpi_install.', f):
            final_fields.append(re.sub(r'mpi_install\.', '', f))
        elif re.match(r'test_build.', f):
            final_fields.append(re.sub(r'test_build\.', '', f))
        elif re.match(r'test_run.', f):
            final_fields.append(re.sub(r'test_run\.', '', f))
        else:
            final_fields.append(f)

    return sql, final_fields
