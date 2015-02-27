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
def post_detail():
    global base_url
    
    s = requests.Session()

    headers = {'content-type': 'application/json'}

    payload = {}

    payload['phases'] = []
    payload['phases'].append( 'install' )

    payload['columns'] = []
    payload['columns'].append( 'mpi_name' )

    payload['search'] = {}
    payload['search']['start_timestamp'] = '2014-10-15 02:00:00'
    payload['search']['end_timestamp']   = '2014-10-15 22:00:00'

    
    url = base_url + "/detail"
    print "URL: " + url
    
    r = s.post(url, data=json.dumps(payload), headers=headers)

    print "Post Detail: %d: %s" % (r.status_code, r.headers['content-type'])
    print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))

################################################################
#
################################################################
def post_complex_detail(phase="install"):
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


    url = base_url + "/detail"
    print "URL: " + url
    
    r = s.post(url, data=json.dumps(payload), headers=headers)

    print "Post Detail: %d: %s" % (r.status_code, r.headers['content-type'])
    result = r.json()
    print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
    
    if result["values"] != None:
        print "Length: " + str( len(result["values"]) )


################################################################
# Main Program
################################################################
#get_fields()
post_detail()
#post_complex_detail("install")
#post_complex_detail("test_build")
#post_complex_detail("test_run")
#post_complex_detail("all")

print "-" * 70

