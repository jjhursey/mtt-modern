#
# Summary reporting
#

import psycopg2

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


def index(db_settings, session=[]):
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
                            " password="+db_settings["password"])
    cur = conn.cursor()

    #
    # Find the necessary values
    #
    sql = """SELECT
             http_username,
             platform_name,
             platform_hardware,
             os_name,
             mpi_name,
             mpi_version,
             (CASE WHEN mpi_install.test_result = 1 THEN 1 ELSE 0 END) as mpi_install_pass,
             (CASE WHEN mpi_install.test_result = 0 THEN 1 ELSE 0 END) as mpi_install_fail,
             (CASE WHEN test_build.test_result = 1 THEN 1 ELSE 0 END) as test_build_pass,
             (CASE WHEN test_build.test_result = 0 THEN 1 ELSE 0 END) as test_build_fail,
             (CASE WHEN test_run.test_result = 1 THEN 1 ELSE 0 END) as test_run_pass,
             (CASE WHEN test_run.test_result = 0 THEN 1 ELSE 0 END) as test_run_fail,
             (CASE WHEN test_run.test_result = 2 THEN 1 ELSE 0 END) as test_run_skip,
             (CASE WHEN test_run.test_result = 3 THEN 1 ELSE 0 END) as test_run_timed
           FROM
              submit JOIN mpi_install using (submit_id)
                     JOIN test_build using (mpi_install_id)
                     JOIN test_run using (test_build_id)
           WHERE
              mpi_install.mpi_install_id > 0"""

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
