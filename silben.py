# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, g, redirect, session, url_for, flash
import shelve
import pymongo

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



def get_db():
    db = getattr(g, '_shelve', None)
    print('get db')
    if db is None:
        uri = 'mongodb://silbenUser_:silbenPwd_@ds027668.mongolab.com:27668/silben'
        conn = pymongo.MongoClient(uri)
        uri_parts = pymongo.uri_parser.parse_uri(uri)
        db = conn[uri_parts['database']]
        #db = g._shelve = shelve.open('config.db')
        if not 'users' in db.collection_names():
            admin = {'username':'admin','pw':generate_password_hash('admin'), 'id':0}
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

@app.route('/_auth/delT/<name>/')
def delT(name):
    sh = get_db()
    if name in sh['users'] and name != 'admin':
        l = sh['users']
        l.pop(name)
        sh['users'] = l
    return redirect(url_for('home'))

@app.route('/_auth/addT/', methods=['GET','POST'])
def addT():
    if request.method == 'POST':
        lname = request.form['lname']
        password = request.form['password']
        db = get_db()
        if lname and db.users.find_one({'username':lname}):
            if g.user['id'] == 0:
                db.users.insert({'username':lname,'pw':generate_password_hash(password), 'times':[]})
                #l[lname] = {'pw':generate_password_hash(password), 'id':1, 'times':[]}
            else:
                db.users.insert({'username':lname,'pw':generate_password_hash(password), 'times':[]})
                #l[lname] = {'pw':generate_password_hash(password), 'id':2, 'times':[]}
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
        #with db.users.find_one({'username':request.form['username']}) as user:
        print(user, check_password_hash(user['pw'], password))
        if user:
            if check_password_hash(user['pw'], password):
                session['user'] = user['username']
            else:
                flash('Name oder Passwort falsch!')
            return redirect(url_for('home'))
        #if username in users and check_password_hash(users[username]['pw'], password):
            #session['user'] = db.users.find_one({'username'
        #else:
            #flash('Name oder Passwort falsch!')
    return redirect(url_for('home'))
    
@app.route('/_auth/logout/')
def logout():
    session.clear()
    return redirect(url_for('home'))

from datetime import datetime
@app.route('/finish')
def finish():
    utime = request.args.get('ti',0,type=int)
    times = session.get('times')
    if not times:
        times = []
    times.append(utime)
    session['times'] = times
    sh = get_db()
    users = sh['users']
    user = users.find_one({'username':g.user})
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
    user = sh['users'].find_one({'username':g.user})
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


