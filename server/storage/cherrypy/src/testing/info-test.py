#
#
#
import requests
import json

base_url = "http://flux.cs.uwlax.edu/~jjhursey/mtt/api"


################################################################
#
################################################################
def post_info_runtime():
    global base_url
    
    s = requests.Session()

    headers = {'content-type': 'application/json'}

    payload = {}

    payload['phases'] = []
    #payload['phases'].append( 'install' )
    #payload['phases'].append( 'test_build' )
    payload['phases'].append( 'test_run' )

    #payload['columns'] = []
    #payload['columns'].append( 'duration' )
    #payload['columns'].append( 'test_suite_name' )
    
    payload['search'] = {}
    payload['search']['start_timestamp'] = '2015-01-01 01:00:00'
    payload['search']['end_timestamp']   = '2015-01-11 01:00:00'
    payload['search']['test_name']       = 'c_hello'
    #payload['search']['test_name']       = 'MPI_Allreduce_c'

    
    url = base_url + "/info/runtime"
    print "URL: " + url
    
    r = s.post(url, data=json.dumps(payload), headers=headers)

    if r.status_code == 200:
        print "Post Summary: %d: %s" % (r.status_code, r.headers['content-type'])
        result = r.json()
        print json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': '))
        print json.dumps(payload, sort_keys=True, indent=4, separators=(',',': '))
    
        if result["values"] != None:
            print "Length: " + str( len(result["values"]) )
    else:
        print "Reason: \"%s\"" % str(r.reason)


################################################################
# Main Program
################################################################
post_info_runtime()

print "-" * 70

