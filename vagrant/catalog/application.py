from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, make_response
from flask import session as login_session
app = Flask(__name__)

import random, string, httplib2, json, requests

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, Category, ItemCategory, User

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

engine = create_engine('sqlite:///itemcatalog.db', echo=True)
Base.metadate.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# response method
def returnResponse(response, code, contentType):
    """Returns HTTP response where response is string, code is int, and
    contentType is a string"""
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
                   picture=login_Session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

# Webhandler for Item Catalog homepage
@app.route('/')
@app.route('/catalog/')
def showHomePage():
    return "Show main homepage, Categories and a list of recently added items"


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
        return returnResponse("Successfully disconnected", 200, "application/json")
    else:
        # given response token invalid for whatever reason / something went wrong
        return returnResponse("Failed to revoke token for given user", 400, "application/json")



@app.route('/catalog/<string:category>/items/')
def showCatalog(category):
    return "Show item list for specific category %s" % category


@app.route('/catalog/<string:category>/<string:item>/')
def showItem(category, item):
    return "Show details for item %s in category %s" % (item, category)


@app.route('/catalog/<string:category>/addItem/')
def addItem(category):
    return "Add new item to category %s" % category


@app.route('/catalog/<string:category>/<string:item>/editItem/')
def editItem(category, item):
    return "Edit details for item %s in category %s" % (item, category)


@app.route('/catalog/<string:category>/<string:item>/deleteItem/')
def deleteItem(category, item):
    return "Delete item %s from category %s" % (item, category)


@app.route('/catalog/<string:category>/json/')
def catalogJSON(category):
    return "Display JSON data for category %s" % category


@app.route('/catalog/<string:category>/<string:item>/json/')
def itemJSON(category, item):
    return "Display JSON data for item %s in category %s" % (item, category)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
