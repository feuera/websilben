# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, g, redirect, session, url_for, flash
import shelve

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
    return silben

@app.before_request
def get_current_user():
    g.user = None
    user = session.get('user')
    if user is not None:
        g.user = user
    silben = get_sh()['silben']
    if silben is not None:
        g.silben = silben 


def get_sh():
    sh = getattr(g, '_shelve', None)
    if sh is None:
        sh = g._shelve = shelve.open('config.db')
        if not 'users' in sh:
            admin = {'admin':{'pw':generate_password_hash('admin'), 'id':'A'}}
            sh['users'] = admin
            print('add user',sh['users'])
        #if not 'silben' in sh: #test for new silben
        silben = getSilben()
        sh['silben'] = silben
    else:
        print(list(sh.keys()))
    return sh

@app.teardown_appcontext
def teardown_sh(exception):
    sh = getattr(g, '_shelve', None)
    if sh is not None:
        sh.close()

@app.route('/_auth/delT/<name>/')
def delT(name):
    sh = get_sh()
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
        sh = get_sh()
        if lname and not lname in sh['users']:
            l = sh['users']
            l[lname] = {'pw':generate_password_hash(password), 'id':'L'}
            sh['users'] = l
        else:
            flash('name doppelt!!')
    return redirect(url_for('home'))


@app.route('/_auth/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        sh = get_sh()
        users = sh['users']
        print(users)

        if username in users and check_password_hash(users[username]['pw'], password):
            currentUser = {}
            currentUser['username'] = request.form['username']
            session['user'] = currentUser
        else:
            flash('Name oder Passwort falsch!')
    return redirect(url_for('home'))
    
@app.route('/_auth/logout/')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/silben/')
def silben():
    return 'silben'

@app.route("/")#, methods=['GET','POST'])
def home():
    return render_template('silben.html')

if __name__ == "__main__":
    app.run(port=3000)


