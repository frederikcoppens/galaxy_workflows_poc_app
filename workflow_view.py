import json
from flask import Flask, render_template, request, flash
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField



class ReusableForm(Form):
    keyword = TextField('Search', validators=[validators.required()])


# preparing data

def get_workflow_data():
    with open('galaxy_workflow_tools_public.json') as f:
        return json.load(f)

def all_tools(data):
    tools = {}
    for key, wf in data.items():
        for tool in wf['tools']:
            tools[tool['id']] = tool['name']
    return tools

def all_workflows(data):
    workflows = {}
    for key, wf in data.items():
        workflows[wf['key']] = wf['name']
    return workflows

def all_users(data):
    users = {}
    for key, wf in data.items():
        if wf['owner'] in users:
            users[wf['owner']].append(wf)
        else:
            users[wf['owner']] = [wf]
    return users

def get_tool_view(data):
    '''
    list of tools with workflows containing that tool
    '''

    tools_view = {}
    for key, wf in data.items():
        for tool in wf['tools']:
            if tool['id'] in tools_view:
                if not wf['key'] in tools_view[tool['id']]:
                    tools_view[tool['id']].append(wf)
            else:
                tools_view[tool['id']] = [wf]
    return tools_view

def get_workflow(data, workflow_key):
    return data[workflow_key]

def get_toollist_for_workflow(data, workflow_key):
    return get_workflow(data, workflow_key)['tools']

def make_search_list(data):
    full_list = {}
    tools =  all_tools(data)
    for tool_id, tool_name in all_tools(data).items():
        if not tool_name in full_list:
            full_list[tool_name] = 'tool/{}'.format(tool_id)
    for workflow_key, workflow_name in all_workflows(data).items():
        if not workflow_name in full_list:
            #TO DO sort out workflows with same name
            full_list[workflow_name] = 'workflow/{}'.format(workflow_key)
    return full_list

def do_search(search_list, value):
    result = []
    for name, link in search_list.items():
        if value.lower() in name.lower():
            result.append({name: link})
    return result

def get_hosts():
    with open('hosts.json', 'rb') as fp:
        return json.loads(fp.read().decode())

hosts = get_hosts()
data = get_workflow_data()
tools_list = all_tools(data)
tools_view = get_tool_view(data)
search_list = make_search_list(data)
userlist = all_users(data)

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d471f274541f27837d44842fb6176a'

@app.route("/")
def home():
    return render_template("home.html", hosts = hosts)

@app.route("/workflows")
def workflows():
    return render_template("workflows.html", workflows = data)

@app.route("/tools")
def tools():
    return render_template("tools.html", tools = tools_list)

@app.route('/workflow/<path:key>', methods=['GET'])
def workflow(key):
    return render_template("workflow.html", tools = get_toollist_for_workflow(data, key), title = get_workflow(data, key)['name'])

@app.route('/tool/<path:tool_id>', methods=['GET'])
def tool(tool_id):
    return render_template("tool.html", workflows = tools_view[tool_id], title = tool_id)

@app.route('/users')
def users():
    return render_template("users.html", userlist = userlist)

@app.route('/user/<path:name>', methods=['GET'])
def user(name):
    return render_template("user.html", workflows = userlist[name], name = name)

@app.route('/index_list')
def index_list():
    return render_template("index_list.html", full_list = search_list)

@app.route('/search', methods=['POST','GET'])
def search():
    form = ReusableForm(request.form)

    print (form.errors)
    if request.method == 'POST':
        keyword=request.form['keyword']
        print (keyword)

        if form.validate():
            # Save the comment here.
            for result in do_search(search_list, keyword):
                for name, link in result.items():
                    flash(name, link)
        else:
            flash('All the form fields are required. ')
    return render_template('search.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)
