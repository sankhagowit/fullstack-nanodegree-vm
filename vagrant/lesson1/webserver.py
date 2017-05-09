from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from urllib import urlencode
from urlparse import urlparse
import bleach

engine = create_engine('sqlite:///restaurantmenu.db',echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsedURL = urlparse(self.path)

            if parsedURL.path.endswith("/hello"):
                # search for url requests which end in /hello
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""  # message to send back to the client
                output += "<html><body>Hello!"
                output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name='message' type='text'><input type='submit' value='Submit'></form>"
                output += "</body></html>"
                self.wfile.write(output)
                print output  # for debugging
                return

            if parsedURL.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurants = session.query(Restaurant).\
                order_by(Restaurant.name)

                output = ""
                output += "<html><body>"

                if restaurants:
                    for restaurant in restaurants:
                        output += "<p>%s<br>" % restaurant.name
                        output += "<a href='/edit?%s'>Edit</a><br>" % restaurant.id
                        output += "<form method='POST' enctype='multipart/form-data' action='/delete'><input type='submit' value='Delete'><input name='id' type='hidden' value='%s'></form>" % restaurant.id

                output += "<a href='/new'>Make a New Restaurant Here</a>"
                output += "</body></html>"

                self.wfile.write(output)
                print output
                return


            if parsedURL.path.endswith("/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaraunt</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/new'><input name='restarauntName' type='text'><input type='submit' value='Create'></form>"
                output += "</body></html>"
                self.wfile.write(output)

                return


            if parsedURL.path.endswith("/edit"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurant_update = session.query(Restaurant).filter_by(id=parsedURL.query).one()

                output = ""
                output += "<html><body>"
                output += "<h1>Update %s Name</h1>" % restaurant_update.name
                output += "<form method='POST' enctype='multipart/form-data' action='/edit'><input name='updateRestaurauntName' type='text' value='%s'><input type='submit' value='Update'><input name='id' type='hidden' value='%s'></form>" % (restaurant_update.name, parsedURL.query)
                output += "</body></html>"
                self.wfile.write(output)

                return


            if parsedURL.path.endswith("/hola"):
                # search for url requests which end in /hola
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""  # message to send back to the client
                output += "<html><body>&#161Hola! <a href='/hello'>Back to Hello</a>"
                output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name='message' type='text'><input type='submit' value='Submit'></form>"
                output += "</body></html>"
                self.wfile.write(output)
                print output  # for debugging
                return

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/new"):
                self.send_response(301)
                self.end_headers()

                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    name = fields.get('restarauntName')

                new_restaraunt = Restaurant(name=name[0])
                session.add(new_restaraunt)
                session.commit()

                restaurants = session.query(Restaurant).\
                order_by(Restaurant.name)
                output = ""
                output += "<html><body><h2>Added %s to List</h2>" % name[0]

                if restaurants:
                    for restaurant in restaurants:
                        output += "<p>%s<br>" % restaurant.name
                        output += "<a href='/edit?%s'>Edit</a><br>" % restaurant.id
                        output += "<form method='POST' enctype='multipart/form-data' action='/delete'><input type='submit' value='Delete'><input name='id' type='hidden' value='%s'></form>" % restaurant.id

                output += "<a href='/new'>Make a New Restaurant Here</a>"
                output += "</body></html>"
                self.wfile.write(output)
                print output


            if self.path.endswith("/edit"):
                self.send_response(301)
                self.end_headers()

                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    name = fields.get('updateRestaurauntName')
                    rest_id = fields.get('id')

                old_restaurant = session.query(Restaurant).filter_by(id=rest_id[0]).one()
                old_restaurant.name = bleach.clean(name[0])
                session.add(old_restaurant)
                session.commit()

                restaurants = session.query(Restaurant).\
                order_by(Restaurant.name)
                output = ""
                output += "<html><body><h2>Updated %s in List</h2>" % name[0]

                if restaurants:
                    for restaurant in restaurants:
                        output += "<p>%s<br>" % restaurant.name
                        output += "<a href='/edit?%s'>Edit</a><br>" % restaurant.id
                        output += "<form method='POST' enctype='multipart/form-data' action='/delete'><input type='submit' value='Delete'><input name='id' type='hidden' value='%s'></form>" % restaurant.id

                output += "<a href='/new'>Make a New Restaurant Here</a>"
                output += "</body></html>"
                self.wfile.write(output)
                print output


            if self.path.endswith("/delete"):
                self.send_response(301)
                self.end_headers()

                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    rest_id = fields.get('id')

                old_restaurant = session.query(Restaurant).filter_by(id=rest_id[0]).one()
                name = old_restaurant.name
                session.delete(old_restaurant)
                session.commit()

                restaurants = session.query(Restaurant).\
                order_by(Restaurant.name)
                output = ""
                output += "<html><body><h2>Deleted %s from List</h2>" % name

                if restaurants:
                    for restaurant in restaurants:
                        output += "<p>%s<br>" % restaurant.name
                        output += "<a href='/edit?%s'>Edit</a><br>" % restaurant.id
                        output += "<form method='POST' enctype='multipart/form-data' action='/delete'><input type='submit' value='Delete'><input name='id' type='hidden' value='%s'></form>" % restaurant.id

                output += "<a href='/new'>Make a New Restaurant Here</a>"
                output += "</body></html>"
                self.wfile.write(output)
                print output


        except:
            pass

def main():
    try:
        port = 8080
        server = HTTPServer(('',port), webServerHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()  # immediately runs the main methods when the python
            # interpreter executes this script.
