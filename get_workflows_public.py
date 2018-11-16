from bioblend import galaxy
import json
import urllib.request

#galaxy_eu = 'http://usegalaxy.eu'
#apikey_eu = 'c2f0ec4f2ffb6f5dd88c98151e8bd9f4'
#gi = galaxy.GalaxyInstance(url=galaxy_eu, key=apikey_eu)
#list_of_workflows = gi.workflows.get_workflows(published=True)


#  "usegalaxy.eu" : "http://usegalaxy.eu",
#  "usegalaxy.org": "http://usegalaxy.org"

def get_hosts():
    with open('hosts.json', 'rb') as fp:
        return json.loads(fp.read().decode())

hosts = get_hosts()
workflows = {}
tools = {}

for host, host_url in hosts.items():

    print("{}: {}".format(host, host_url))
    workflow_url = '{}/api/workflows'.format(host_url)
    #print(workflow_url)
    with urllib.request.urlopen(workflow_url) as h:
        list_of_workflows = json.loads(h.read().decode())

    for w in list_of_workflows:
        # only the published ones, not private ones
        workflow_id = w['id']
        workflow_name = w['name']
        workflow_owner = w['owner']

        show_workflow_url = '{}/api/workflows/{}'.format(host_url, workflow_id)
        with urllib.request.urlopen(show_workflow_url) as h:
            show_workflow = json.loads(h.read().decode())

        key = host + "_" + workflow_id
        #print("{}: {}".format(workflow_id, workflow_name))

        thisworkflow_tools = []
        for index, step in show_workflow['steps'].items():
            if step['type'] == 'tool':
                # get tool info through API
                if step['tool_id'] in tools:
                    print("\t{} already fetched".format(step['tool_id']))
                    pass
                else:
                    tool_url = "{}/api/tools/{}".format(host_url, urllib.parse.quote(step['tool_id']))
                    print("\t{}".format(tool_url))
                    tool_name = "not available"
                    try:
                        with urllib.request.urlopen(tool_url) as url:
                            tool_json = json.loads(url.read().decode())
                        tool_name = tool_json['name']
                    except urllib.error.HTTPError:
                        print("\t404 : {}".format(tool_url))
                        print("\tTool not found: removing workflow")
                        del workflows[w['name']]
                        break
                    tool_info = {
                        'id': step['tool_id'],
                        'name': tool_name
                    }
                    tools[step['tool_id']] = tool_info
                    thisworkflow_tools.append(tools[step['tool_id']])

        workflows[key] = {
            'tools': thisworkflow_tools ,
            'host': host,
            'id': workflow_id,
            'key': key,
            'name' : workflow_name,
            'owner' : workflow_owner,
        }
    print("Total: {}".format(len(workflows)))

    with open('galaxy_workflow_tools_public.json', 'w') as fp:
        json.dump(workflows, fp, indent=4, sort_keys=True)
