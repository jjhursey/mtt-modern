#
#
#
import requests
import json

#server_addr = "flux.cs.uwlax.edu"
server_addr = "138.49.30.31"
server_port = 9090

base_url = "http://" + server_addr + ":" + str(server_port)


################################################################
#
################################################################
def get_fields():
    global base_url
    
    s = requests.Session()

    url = base_url + "/fields"
    print "URL: " + url
    r = s.get(url)

    print "Get Fields: %d: %s" % (r.status_code, r.headers['content-type'])
    print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))


################################################################
#
################################################################
def get_summary():
    global base_url
    
    s = requests.Session()

    payload = {'phases': 'install'}
    url = base_url + "/summary"
    print "URL: " + url
    
    r = s.get(url, params=payload)

    print "Get Summary: %d: %s" % (r.status_code, r.headers['content-type'])
    print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))


################################################################
#
################################################################
def post_summary():
    global base_url
    
    s = requests.Session()

    headers = {'content-type': 'application/json'}

    payload = {}

    payload['phases'] = []
    #payload['phases'].append( 'install' )
    #payload['phases'].append( 'test_build' )
    payload['phases'].append( 'test_run' )
    #payload['phases'].append( 'all' )

    payload['columns'] = []
    payload['columns'].append( 'http_username' )
    payload['columns'].append( 'platform_name' )
    payload['columns'].append( 'platform_hardware' )
    payload['columns'].append( 'os_name' )
    payload['columns'].append( 'mpi_name' )
    payload['columns'].append( 'mpi_version' )
    payload['columns'].append( 'bitness' )
    #payload['columns'].append( 'endian' )
    #payload['columns'].append( 'bitness' )
    #payload['columns'].append( 'vpath_mode' )
    #payload['columns'].append( 'duration' )
    #payload['columns'].append( 'test_suite_name' )
    payload['columns'].append( 'compiler_name' )
    payload['columns'].append( 'compiler_version' )
    payload['columns'].append( 'test_suite_name' )
    
    payload['search'] = {}
    payload['search']['start_timestamp'] = '2014-10-15 02:00:00'
    payload['search']['end_timestamp']   = '2014-10-15 22:00:00'
    #payload['search']['test_suite_name']   = 'trivial'
    payload['search']['compiler_name']   = 'gnu'
    #payload['search']['mpi_install_pass'] = 1
    #payload['search']['mpi_install_fail'] = 0
    #payload['search']['test_build_pass'] = 1
    #payload['search']['test_build_fail'] = 1
    #payload['search']['test_run_pass'] = 1
    #payload['search']['test_run_fail'] = 1
    #payload['search']['test_run_skip'] = 1
    #payload['search']['test_run_timed'] = 1

    
    url = base_url + "/summary"
    print "URL: " + url
    
    r = s.post(url, data=json.dumps(payload), headers=headers)

    print "Post Summary: %d: %s" % (r.status_code, r.headers['content-type'])
    result = r.json()
    print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
    print json.dumps(payload, sort_keys=True, indent=4, separators=(',',': '))
    
    if result["values"] != None:
        print "Length: " + str( len(result["values"]) )

################################################################
#
################################################################
def post_summary_options():
    global base_url
    
    s = requests.Session()

    headers = {'content-type': 'application/json'}

    payload = {}

    payload['options'] = {}
    payload['options']['count_only'] = 1
    #payload['options']['limit'] = 5
    payload['options']['offset'] = 0

    payload['phases'] = []
    #payload['phases'].append( 'install' )
    #payload['phases'].append( 'test_build' )
    payload['phases'].append( 'test_run' )
    #payload['phases'].append( 'all' )

    payload['columns'] = []
    payload['columns'].append( 'mpi_name' )
    #payload['columns'].append( 'endian' )
    #payload['columns'].append( 'bitness' )
    #payload['columns'].append( 'vpath_mode' )
    #payload['columns'].append( 'duration' )
    payload['columns'].append( 'test_suite_name' )
    #payload['columns'].append( 'compiler_name' )

    payload['search'] = {}
    payload['search']['start_timestamp'] = '2014-10-15 02:00:00'
    payload['search']['end_timestamp']   = '2014-10-15 22:00:00'
    #payload['search']['test_suite_name']   = 'trivial'
    #payload['search']['compiler_name']   = 'gnu'
    #payload['search']['mpi_install_pass'] = 1
    #payload['search']['mpi_install_fail'] = 0
    #payload['search']['test_build_pass'] = 1
    #payload['search']['test_build_fail'] = 1
    #payload['search']['test_run_pass'] = 1
    #payload['search']['test_run_fail'] = 1
    #payload['search']['test_run_skip'] = 1
    #payload['search']['test_run_timed'] = 1

    
    url = base_url + "/summary"
    print "URL: " + url
    
    r = s.post(url, data=json.dumps(payload), headers=headers)

    print "Post Summary: %d: %s" % (r.status_code, r.headers['content-type'])
    result = r.json()
    print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
    
    if result["values"] != None:
        print "Length: " + str( len(result["values"]) )


################################################################
#
################################################################
def post_complex_summary(phase="install"):
    global base_url
    
    s = requests.Session()

    headers = {'content-type': 'application/json'}
    payload = {}

    
    ###############################
    # What phases are we looking for
    # Create a 'set'/'dictionary' for the parameters
    ###############################
    payload['phases'] = []
    payload['phases'].append(phase)

    
    ###############################
    # What fields we want returned
    # Do not need to specify the aggregation fields (test_run_pass, ...)
    ###############################
    payload['columns'] = []
    payload['columns'].append('http_username')
    payload['columns'].append('platform_name')
    payload['columns'].append('platform_hardware')
    payload['columns'].append('os_name')
    payload['columns'].append('mpi_name')
    payload['columns'].append('mpi_version')
    payload['columns'].append('compiler_name')

    if phase == "test_build":
        payload['columns'].append('test_suite_name')
        
    ###############################
    # What are the search parameters
    ###############################
    payload['search'] = {}
    
    # today
    # yesterday
    # past 12 hours
    # past 24 hours
    # past 2 days
    # past 1 week
    #payload['relative_timestamp'] = 'past 24 hours'

    # Date Range
    payload['search']['start_timestamp'] = '2014-10-15 02:00:00'
    payload['search']['end_timestamp']   = '2014-10-15 22:00:00'

    # Org
    payload['search']['http_username'] = 'nvidia'

    # Platform information
    #    Name
    #payload['search']['platform_name'] = 'ivy cluster'
    #    Hardware
    #payload['search']['platform_hardware'] = 'x86_64'
    # OS
    #payload['search']['os_name'] = 'Linux'


    # Compiler
    payload['search']['compiler_name'] = 'gnu'


    # MPI Version
    #payload['search']['mpi_version'] = 'v1.8.3-37-g9208601'

    # MPI Name
    payload['search']['mpi_name'] = 'ompi-v1.8'


    url = base_url + "/summary"
    print "URL: " + url
    
    r = s.post(url, data=json.dumps(payload), headers=headers)

    print "Post Summary: %d: %s" % (r.status_code, r.headers['content-type'])
    result = r.json()
    print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
    
    if result["values"] != None:
        print "Length: " + str( len(result["values"]) )


################################################################
# Main Program
################################################################
#get_fields()
#get_summary()
#post_summary()
#post_summary_options()
#post_complex_summary("install")
#post_complex_summary("test_build")
#post_complex_summary("test_run")
#post_complex_summary("all")

print "-" * 70
