from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, make_response
from flask import session as login_session
app = Flask(__name__)

import random, string, httplib2, json, requests
from sqlalchemy import create_engine, desc, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, Category, User

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

engine = create_engine('sqlite:///itemcatalog.db', echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# response method
def returnResponse(response, code, contentType):
    """Returns HTTP response where response is th e response message as a
    string, code is int, and contentType is the header Content-Type as
    a string"""
    response = make_response(json.dumps(response), code)
    response.headers['Content-Type'] = contentType
    return response

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    print "New user %s created!" % login_session['email']
    return user.id


# Webhandler for Item Catalog homepage
@app.route('/')
@app.route('/catalog/')
def showHomePage():
    # Check if user is logged in or not
    title = "Latest Items"
    categories = session.query(Category).order_by(Category.name).all()
    items = session.query(Item).order_by(desc(Item.id)).all()
    if 'username' not in login_session:
        return render_template('latest.html', title=title, items=items,
                               categories=categories)
    else:
        user = getUserInfo(getUserID(login_session['email']))
        return render_template('latest.html', title=title, items=items,
                               user=user, categories=categories)


@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
@app.route('/gconnect', methods=["POST"])
def gconnect():
    if request.args.get('state') != login_session['state']:
        print "Invalid State Parameter"
        return returnResponse("Invalid State Parameter", 401, "application/json")

    code = request.data # proceed, collect one time code from server
    # try to use this one time code to get a token
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        # specify w/ postmessage this is one time code flow server will send off
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)   # initiate exchange
        # exchanges one time code authorizatino for a credentials object
    except FlowExchangeError:
        print "Failed to upgrade the authorization code"
        return returnResponse("Failed to upgrade the authorization code", 401,
                              "application/json")

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1]) #verify with google api server that token is valid for use with JSON 'GET' request

    if result.get('error') is not None:
        print "error in server fetching data from google api"
        return returnResponse("Error in server fetching data from google api", 500,
                              "application/json")

    # Verify that the access token is used for the intended use... by matching user credentials
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        print "Token's user id doesn't match the given user id"
        return returnResponse("Token's user id doesn't match the given user id", 401,
                              "application/json")

    if result['issued_to'] != CLIENT_ID:
        print "Token's client ID does not match app's"
        return returnResponse("Token's Client ID does not match app's", 401,
                              "application/json")

    # Check to see if the user is already logged into the system
    stored_credentials = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        print "Current user already connected"
        return returnResponse("Current user already connected", 200,
                              "application/json")

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # get user Information using google+ api.. send request to google server
    # using the access token that we got from google.
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt':'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    # See if user exists, if they do not, make a new one in user database
    user_id = getUserID(login_session['email'])
    print "call to check user_id found: " + str(user_id)
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user
    credentials = login_session.get('access_token')
    if credentials is None:
        return returnResponse("Current user not connected", 401, "application/json")

    # Execute HTTP GET request to revoke current token
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0] # googles response

    if result['status'] == '200':
        # reset the user's session.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        flash('Successfully disconnected')
        return redirect(url_for('showHomePage'))
    else:
        # given response token invalid for whatever reason / something went wrong
        return returnResponse("Failed to revoke token for given user", 400, "application/json")


@app.route('/catalog/<string:category>/items/')
def showCatalog(category):
    title = "%s Item Catalog" % category
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category_name=category).all()
    if 'username' not in login_session:
        # Need own HTML template which will have the add button for the items
        return render_template('singleCatalog.html', title=title, items=items, categories=categories, category=category)
    else:
        user = getUserInfo(getUserID(login_session['email']))
        return render_template('singleCatalog.html', title=title, items=items, user=user, categories=categories, category=category)


@app.route('/catalog/<string:category>/<string:item>/')
def showItem(category, item):
    title = "%s Item Catalog" % category
    categories = session.query(Category).all()
    item = session.query(Item).filter_by(name=item).one()
    if 'username' not in login_session:
        return render_template('item.html', title=title, item=item,
                               categories=categories)
    else:
        user = getUserInfo(getUserID(login_session['email']))
        return render_template('item.html', title=title, item=item,
                               user=user, categories=categories)


@app.route('/catalog/<string:category>/addItem/', methods=["GET", "POST"])
def addItem(category):
    if 'username' not in login_session:
        flash('Must be logged in to add an item')
        return redirect(url_for('showCatalog', category=category))

    if request.method == "POST":
        if request.form['name']:
            if request.form['description']:
                if request.form['category']:
                    if not session.query(Item).filter_by(name=request.form['name']).first():
                        newItem = Item(name=request.form['name'],
                                       description=request.form['description'],
                                       category_name=request.form['category'],
                                       author=login_session['email'])
                        session.add(newItem)
                        session.commit()
                        flash('%s item created!' % newItem.name)
                        return redirect(url_for('showItem', category=newItem.category_name, item=newItem.name))
                    else:
                        flash('Item %s already exists! Cannot create another' % request.form['name'])
                        return redirect(url_for('addItem', category=category))
    else:
        title = "Add New Item"
        categories = session.query(Category).all()
        user = getUserInfo(getUserID(login_session['email']))
        return render_template('addItem.html', title=title, user=user, categories=categories, category=category)

    flash('To create new item all fields must be completed (name, description, category')
    return redirect(url_for('addItem', category=category))



@app.route('/catalog/<string:category>/<string:item>/editItem/', methods=["GET", "POST"])
def editItem(category, item):
    if 'username' not in login_session:
        flash('Must be logged in to edit an item')
        return redirect(url_for('showCatalog', category=category))
    item = session.query(Item).filter_by(name=item).one()
    if item.author != login_session['email']:
        flash('Cannot edit an item you did not create')
        return redirect(url_for('showItem', category=category, item=item.name))
    # Check if it is a get or a post method,
    if request.method == "POST":
        if request.form['description'] != item.description:
            item.description = request.form['description']
        if request.form['category'] != item.category_name:
            item.category_name = request.form['category']
        session.add(item)
        session.commit()
        flash('%s item updated!' % item.name)
        return redirect(url_for('showItem', category=item.category_name, item=item.name))
    else:
        title = "Edit Item %s" % item.name
        categories = session.query(Category).all()
        user = getUserInfo(getUserID(login_session['email']))
        return render_template('editItem.html', title=title, item=item, user=user, categories=categories)



@app.route('/catalog/<string:category>/<string:item>/deleteItem/', methods=["GET", "POST"])
def deleteItem(category, item):
    if 'username' not in login_session:
        flash('Must be logged in to delete an item')
        return redirect(url_for('showCatalog', category=category))
    item = session.query(Item).filter_by(name=item).one()
    if item.author != login_session['email']:
        flash('Cannot delete an item you did not create')
        return redirect(url_for('showItem', category=category, item=item.name))
    # Check if it is a get or a post method,
    if request.method == "POST":
        # if post delete the entry
        session.delete(item)
        session.commit()
        flash('Item %s successfully deleted' % item.name)
        return redirect(url_for('showCatalog', category=category))
    else:
        # if get, display the page
        title = "Delete Item %s" % item.name
        categories = session.query(Category).all()
        user = getUserInfo(getUserID(login_session['email']))
        return render_template('deleteItem.html', title=title, item=item, user=user, categories=categories)


@app.route('/catalog/<string:category>/json/')
def catalogJSON(category):
    if 'username' not in login_session:
        flash('must be logged in to do that')
        return redirect('/')
    catalog = session.query(Category).filter_by(name=category).one()
    items = session.query(Item).filter_by(category_name=category).all()
    return jsonify(catalog = [catalog.serialize], items = [i.serialize for i in items])


@app.route('/catalog/<string:category>/<string:item>/json/')
def itemJSON(category, item):
    if 'username' not in login_session:
        flash('must be logged in to do that')
        return redirect('/')
    item = session.query(Category).filter_by(name=item).one()
    return jsonify(item = [item.serialize])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
