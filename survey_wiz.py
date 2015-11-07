# -*- coding: utf-8 -*-
"""
    Survey Wizard
    ~~~~~~~~
    A survey platform written with Flask and pymongo. It facilitates survey taking and creation.
    :copyright: (c) 2015 by Timur Bagas.
    :license: BSD, see LICENSE for more details.
"""

import time

from pymongo import MongoClient
from bson.objectid import ObjectId
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash

# configuration
"""
DATABASE = '/tmp/minitwit.db'
PER_PAGE = 30
"""
DEBUG = True
SECRET_KEY = 'development key'

# create our little application :)
app = Flask(__name__)
mongo = MongoClient()
app.config.from_object(__name__)
#app.config.from_envvar('MINITWIT_SETTINGS', silent=True)


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    mongo = MongoClient()
    db = mongo['survey-database']
    return db

@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    mongo.close()
    mongo = None

"""
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
"""

"""
@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database.')
"""

"""WARNING"""
"""
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv
"""

"""WARNING"""
def get_user_id(username):
    db = get_db()
    result = db.users.find_one({"username" : username})
    if result != None:
        return result["_id"]
    return None


def get_user_name(username):
    db = get_db()
    result = db.users.find_one({"username" : username})
    if result != None:
        return result["_id"]
    return None

"""
???
def format_datetime(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')
"""

"""
???
def gravatar_url(email, size=80):
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)
"""

"""TODO"""
@app.before_request
def before_request():
    g.user = None
    if '_id' in session:
        db = get_db()
        g.user = db.users.find_one({"_id" : ObjectId(session['_id'])})




@app.route('/')
def index():    
    print "haha"
    if g.user != None:
        return render_template('hello.html', username=str(g.user[unicode("username")]))
    return redirect(url_for('login'))


"""
???
@app.route('/public')
def public_timeline():
    return render_template('timeline.html', messages=query_db('''
        select message.*, user.* from message, user
        where message.author_id = user.user_id
        order by message.pub_date desc limit ?''', [PER_PAGE]))
"""

"""
???
@app.route('/<username>')
def user_timeline(username):
    profile_user = query_db('select * from user where username = ?',
                            [username], one=True)
    if profile_user is None:
        abort(404)
    followed = False
    if g.user:
        followed = query_db('''select 1 from follower where
            follower.who_id = ? and follower.whom_id = ?''',
            [session['user_id'], profile_user['user_id']],
            one=True) is not None
    return render_template('timeline.html', messages=query_db('''
            select message.*, user.* from message, user where
            user.user_id = message.author_id and user.user_id = ?
            order by message.pub_date desc limit ?''',
            [profile_user['user_id'], PER_PAGE]), followed=followed,
            profile_user=profile_user)
"""

"""
???
@app.route('/<username>/follow')
def follow_user(username):
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    db = get_db()
    db.execute('insert into follower (who_id, whom_id) values (?, ?)',
              [session['user_id'], whom_id])
    db.commit()
    flash('You are now following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))
"""

"""
???
@app.route('/<username>/unfollow')
def unfollow_user(username):
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    db = get_db()
    db.execute('delete from follower where who_id=? and whom_id=?',
              [session['user_id'], whom_id])
    db.commit()
    flash('You are no longer following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))
"""

"""
???
@app.route('/add_message', methods=['POST'])
def add_message():
    if 'user_id' not in session:
        abort(401)
    if request.form['text']:
        db = get_db()
        db.execute('''insert into message (author_id, text, pub_date)
          values (?, ?, ?)''', (session['user_id'], request.form['text'],
                                int(time.time())))
        db.commit()
        flash('Your message was recorded')
    return redirect(url_for('timeline'))
"""

@app.route('/create_survey', methods=['GET', 'POST'])
def create_survey():
    if '_id' not in session:
        abort(401)
    else:
        flash("You are now creating a survey!")
    return redirect(url_for('index'))

"""
TODO
"""
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = get_db().users.find_one({"username" : request.form['username']})
        """
        query_db('''select * from user where
        username = ?''', [request.form['username']], one=True)
        """
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['pw_hash'], request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['_id'] = str(user['_id'])
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

"""
TODO
"""
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            db = get_db()
            db.users.insert( \
                {"username" : request.form['username'], \
                "email" : request.form['email'], \
                "pw_hash" : generate_password_hash(request.form['password']), \
                "is_surveyor" : request.form['is_surveyor'] } \
            )
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)

"""
TODO
"""
@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

# add some filters to jinja
"""
???
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url
"""