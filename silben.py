# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, g, redirect, session, url_for, flash
import shelve
import pymongo
import os

#conn = pymongo.MongoClient('mongodb://silbenUser_:silbenPwd_@ds027668.mongolab.com:27668/silben')
#uri_parts = pymongo.uri_parser.parse_uri('mongodb://silbenUser_:silbenPwd_@ds027668.mongolab.com:27668/silben')
#db = conn[uri_parts['database']]
#collection = db.test_collection
#collection.insert({'test':'hello world'})
#post = {"author": "Mike","text": "My first blog post!","tags": ["mongodb", "python", "pymongo"],"date": datetime.datetime.utcnow()}
#posts = db.posts
#post_id = posts.insert(post)
#db.collection_names()

from werkzeug.security import generate_password_hash, \
     check_password_hash

app = Flask(__name__)
app.config.update(
        DEBUG=True,
        SECRET_KEY="mysecrettestkey12_=$",
        )

def getSilben():
    f = open('static/silbenteppich_1.txt','r')
    #print(f.read())
    silben = f.read().split()
    print('silben: ',silben)
    return silben

def getStufen():
    db = get_db()
    print(db)
    stufen = db.stufen.find()
    stufeD = { x['stufe']:x['silben'] for x in stufen}
    return stufeD

@app.before_request
def get_current_user():
    g.user = None
    user = session.get('user')
    if user is not None:
        g.user = user
    silben = session.get('silben')
    if not silben:
        silben = getSilben()
        session['silben'] = silben
    g.silben = silben
    g.stufen = session['stufen'] = getStufen()

def get_db():
    db = getattr(g, '_shelve', None)
    #print('get db')
    if db is None:
        #uri = 'mongodb://silbenUser_:silbenPwd_@ds027668.mongolab.com:27668/silben'
        uri = os.environ['MONGO_DATABASE']
        print('connecting to ',uri)
        conn = pymongo.MongoClient(uri)
        #uri_parts = pymongo.uri_parser.parse_uri(uri)
        db = conn.silben
        #db = g._shelve = shelve.open('config.db')
        if not 'users' in db.collection_names():
            admin = {'username':'admin','pw':generate_password_hash('admin'), 'id':0, 'parent':None}
            users = db.users
            users.insert(admin)
            #db['users'] = admin
            #print('add user',db['users'])
        #if not 'silben' in db: #test for new silben
        #silbenLevel1 = getSilben()
        #silbDb = db.silben
        #db['silben'] = silben
    #else:
        #print(list(db))
    return db

@app.teardown_appcontext
def teardown_sh(exception):
    #print('teardown')
    sh = getattr(g, '_shelve', None)
    if sh is not None:
        sh.close()

def updateSession(user):
    db = get_db()
    usr = db.users.find_one({'username':user})
    childs = {x['username']:{'level':1, 'times':x['times']} for x in db.users.find({'parent':user}) if x}
    print(childs)
    session['user'] = {'username':user, 
            'parent':usr['parent'],
            'childs':childs,
            }

@app.route('/_auth/delT/<name>/')
def delT(name):
    db = get_db()
    db.users.remove({'username':name})
    updateSession(g.user['username'])
    return redirect(url_for('home'))

@app.route('/addN/', methods=['GET','POST'])
def addN():
    if request.method == 'POST':
        stufe = request.form['stufenName'].replace(' ','_')
        silben = request.form['silben'].split('\n')
        #stufeD = {stufe: silben}
        db = get_db()
        print(list(db.stufen.find({'stufe':stufe})))
        if (list(db.stufen.find({'stufe':stufe}))):
            flash("stufe existiert bereits")
        else:
            db.stufen.insert({'stufe':stufe, 'silben':silben})
    return redirect(url_for('home'))

@app.route('/delS/<stufe>')#, methods=['GET','POST'])
def delS(stufe):
    db = get_db()
    db.stufen.remove({'stufe':stufe}) 
    return redirect(url_for('home'))

@app.route('/addS/', methods=['GET','POST'])
def addS():
    if request.method == 'POST':
        silbs = request.form['silben'].split('\n')
        print(silbs)
    return redirect(url_for('home'))

@app.route('/_auth/addT/', methods=['GET','POST'])
def addT():
    if request.method == 'POST':
        lname = request.form['lname']
        password = request.form['password']
        db = get_db()
        if lname and not db.users.find_one({'username':lname}) :
            db.users.insert({'username':lname,'pw':generate_password_hash(password), 'times':[],'parent':g.user['username']})
            updateSession(g.user['username'])
        else:
            flash('name doppelt!!')
    return redirect(url_for('home'))


@app.route('/_auth/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.users.find_one({'username': request.form['username']})
        if user:
            print(user, check_password_hash(user['pw'], password))
            if check_password_hash(user['pw'], password):
                updateSession(request.form['username'])
            else:
                flash('Name oder Passwort falsch!')
            return redirect(url_for('home'))
        else:
            flash('Name und oder Passwort falsch!')
    return redirect(url_for('home'))
    
@app.route('/_auth/logout/')
def logout():
    session.clear()
    return redirect(url_for('home'))

from datetime import datetime
@app.route('/finish')
def finish():
    if not g.user:
        return ''
    utime = request.args.get('ti',0,type=int)
    times = session.get('times')
    if not times:
        times = []
    times.append(utime)
    session['times'] = times
    sh = get_db()
    users = sh['users']
    user = users.find_one({'username':g.user['username']})
    if not user:
        return ''
    if not 'times' in user:
        user['times'] = [] #[datetime.now()]
        #print("add times to user")
    user['times'].append((datetime.now(), utime))
    users.update({'username':user['username']}, user)
    return ''

@app.route("/getTimes/")
def getTimes():
    sh = get_db()
    if not g.user:
        return render_template('table.html')
    user = sh.users.find_one({'username':g.user['username']})
    if not user and session.get('times'):
        return render_template('table.html', times=session['times'])
    if 'times' in user:
        return render_template('table.html', times=user['times'])
    return render_template('table.html')

#@app.route('/silben/')
#def silben():
    #return 'silben'

@app.route("/")#, methods=['GET','POST'])
def home():
    return render_template('silben.html')

if __name__ == "__main__":
    #app.run(port=3000)
    app.run()


