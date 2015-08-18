#
# Validation
#

import string
import re


def validate_search_parameters(_db, _logger, session, data, is_summary=True):
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
        tables = _db.which_table_contains(col)
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
        tables =  _db.which_table_contains(col)
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

