from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, make_response
from flask import session as login_session
app = Flask(__name__)

import random, string, httplib2, json, requests

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#from database_setup import Base, Item, Category, ItemCategory

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

# engine = create_engine('sqlite:///itemcatalog.db', echo=True)
# Base.metadate.bind = engine
# DBSession = sessionmaker(bind=engine)
# session = DBSession()

# Webhandler for Item Catalog homepage
@app.route('/')
@app.route('/catalog/')
def showHomePage():
    return "Show main homepage, Categories and a list of recently added items"


@app.route('/login/')
def login():
    return "Show Login Page"


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


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
