from flask import Flask, request
import json
from bson import json_util
from bson.objectid import ObjectId
from pymongo import Connection
from flask import render_template
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

# Flask
app = Flask(__name__, static_url_path='/static')
app.debug = True

# MongoDB connection
connection = Connection('10.8.8.111', 27017)
db = connection.onionsBackupOnline
print("connect to database --> ")

def toJson(data):
    """Convert Mongo object(s) to JSON"""
    return json.dumps(data, default=json_util.default)

@app.route('/events/', methods=['GET'])
def eventsFlow():
    """Return a list of all events
       API GET /events/?limit=10&offset=20
    """
    if request.method == 'GET':
        lim = int(request.args.get('limit', 10))
        off = int(request.args.get('offset', 0))
        results = db['events'].find().skip(off).limit(lim)
        json_results = []
        for result in results:
            json_results.append(result)
        return toJson(json_results)

@app.route('/userinfo/<name>', methods=['GET'])
def userinfo(name):
    """Return specific UFO sighting
       ex) GET /userinfo/diggzhang
    """
    if request.method == 'GET':
        result = db['users'].find_one({'name': name})
    # return toJson(result)
    return render_template('userinfo.html', userinfo=toJson(result))

@app.route('/trackme/<name>', methods=['GET'])
def trackme(name):
    """Return this user's events
       ex) GET /trackme/diggzhang@gmail.com
    """
    if request.method == 'GET':
        result = db['users'].find_one({'name': name})
        userId = result['_id']
        events = db['events'].find({'user': userId}).limit(50)
        eventsList = []
        for event in events:
            eventsList.append(event)
    # return toJson(userId)
    return render_template('trackme.html', eventsFlow=eventsList)

@app.route('/trackme/', methods=['POST'])
def trackuser():
    name = request.form['projectFilepath']
    result = db['users'].find_one({'name': name})
    if result == None:
        msg = "Not found this user name"
        return render_template('trackme.html', msg=msg)
    userId = result['_id']
    events = db['events'].find({'user': userId, "category": {"$nin":["site"]} }).limit(50)
    eventsList = []
    for event in events:
        eventsList.append(event)
    return render_template('trackme.html', eventsFlow=eventsList)

@app.route('/', methods=['GET'])
def homePage():
    if request.method == 'GET':
        return render_template('home.html')

if __name__ == '__main__':
  app.run(debug=True)
