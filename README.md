# Galaxy Workflows

Flask proof-of-concept app to list published workflows of a Galaxy instance and provide a list of tools for each, associate the user and do a basic search.

## Usage

* Clone the repository
* To use with real-life data (skip to use example data):
  - Update hosts.json with the Galaxy instances you want to query (requires /workflows API endpoint to be exposed, expected in 19.01, see [PR](https://github.com/galaxyproject/galaxy/pull/7020))
  - ```python get_workflows_public.py```  to build new galaxy_workflow_tools_public.json
* ```python workflow_view.py```
* Go to http://127.0.0.1:5000
