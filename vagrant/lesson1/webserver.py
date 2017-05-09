from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # search for url requests which end in /hello
            if self.path.endswith("/hello"):
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

            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurants = session.query(Restaurant).\
                order_by(Restaurant.name)

                output = ""
                output += "<html><body>"

                if restaurants:
                    for restaurant in restaurants:
                        output += "<p>%s<br><a href='#'>Edit</a><br><a href='#'>Delete</a></p>" % restaurant.name

                output += "<a href='/new'>Make a New Restaurant Here</a>"
                output += "</body></html>"

                self.wfile.write(output)
                print output
                return


            if self.path.endswith("/new"):
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


            # search for url requests which end in /hola
            if self.path.endswith("/hola"):
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
                        output += "<p>%s<br><a href='#'>Edit</a><br><a href='#'>Delete</a></p>" % restaurant.name

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
                    name = fields.get('restarauntName')

                output = ""
                output += "<html><body>"
                output += "<h2> OLD, how about this: </h2>"
                output += "<h1> %s </h1>" % name[0]
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
