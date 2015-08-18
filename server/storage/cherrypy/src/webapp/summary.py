#
# Summary reporting
#

import psycopg2
import string
import re

import data_pg_flat

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
    if 'options' not in data:
        if len(data) != 3:
            rtn['status'] = -2
            rtn['status_msg'] = "Validate Error: Expected exactly 3 fields. %d supplied." % (len(data))
            return rtn
    else:
        if len(data) != 4:
            rtn['status'] = -2
            rtn['status_msg'] = "Validate Error: Expected exactly 3 fields other than the options field. %d supplied." % (len(data))
            return rtn

    #
    # Check options
    #
    if 'options' in data and "offset" in data['options']:
        if data['options']['offset'] < 0:
            rtn['status'] = -10
            rtn['status_msg'] = "Validate Error: Options parameter 'offset' must be 0 or greater. %d supplied." % ( data['options']['offset'] )
            return rtn
    if 'options' in data and "limit" in data['options']:
        if data['options']['limit'] < 0:
            rtn['status'] = -10
            rtn['status_msg'] = "Validate Error: Options parameter 'limit' must be 0 or greater. %d supplied." % ( data['options']['limit'] )
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
        tables = data_pg_flat.which_table_contains(col)
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
        tables =  data_pg_flat.which_table_contains(col)
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
    sql, fields = data_pg_flat.build_summary_sql(session, data)
    if None == sql:
        return { "fields" : fields, "values" : None }
    print "SQL: \n" + sql
    cur.execute(sql +";")
    rows = cur.fetchall()

    if 'options' in data and "count_only" in data['options']:
        fields = ["count"]
        rows = [ [ len(rows) ] ]

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

def preprocess_field(field):
    if field == "start_timestamp":
        return "start_timestamp"
    elif field == "end_timestamp":
        return "start_timestamp"
    else:
        return field

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

