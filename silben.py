# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, g, redirect, session
import shelve

from werkzeug.security import generate_password_hash, \
     check_password_hash

app = Flask(__name__)
app.config.update(
        DEBUG=True,
        SECRET_KEY="mysecrettestkey",
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
            admin = {'admin':generate_password_hash('admin')}
            sh['users'] = admin
        print(sh['users'])
        #if not 'silben' in sh: #test for new silben
        silben = getSilben()
        sh['silben'] = silben
        #print(sh['silben'])
    return sh

@app.teardown_appcontext
def teardown_sh(exception):
    sh = getattr(g, '_shelve', None)
    if sh is not None:
        sh.close()

@app.route('/_auth/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        sh = get_sh()
        users = sh['users']
        print(users, request.form)
        if username in users and check_password_hash(users[username], password):
            currentUser = {}
            currentUser['username'] = request.form['username']
            session['user'] = currentUser
    return redirect('/')
    
@app.route('/_auth/logout/')
def logout():
    session.clear()
    return redirect('/')

@app.route('/silben/')
def silben():
    return 'silben'

@app.route("/")#, methods=['GET','POST'])
def home():
    return render_template('silben.html')

if __name__ == "__main__":
    app.run()


