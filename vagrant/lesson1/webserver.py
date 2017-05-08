from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # search for url requests which end in /hello
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""  # message to send back to the client
                output += "<html><body>Hello!</body></html>"
                self.wfile.write(output)
                print output  # for debugging
                return

        except IOError:
            self.send_error(404, "File Not FOund %s" % self.path)

def main():
    try:
        port = 8080
        server = HTTPServer(('',port), webserverHandler)
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()  # immediately runs the main methods when the python
            # interpreter executes this script.
