from http.server import HTTPServer, BaseHTTPRequestHandler
from ui_tools import present_menu

# Specify port for HTTP server
PORT = 8000


# Subclass the base handler to implement custom GET and POST handlers
class HTTPRequestHandler(BaseHTTPRequestHandler):

    # Basic GET handler that acknowledges request
    def do_GET(self):
        print("Incoming GET request.")
        for header, value in self.headers.items():
            print(f"{header}: {value}")
        self.send_response(200) # Send 200 OK code
        self.end_headers() # Signal end of response headers
        # Use 'wfile' stream to return response message with default encoding
        self.wfile.write("GET Request received".encode())

    # Handles POST requests that send an image via 'curl'
    # 'curl' command: curl -X POST --data-binary "@/image_path" http://localhost:PORT
    def do_POST(self):
        print("Incoming POST request.")
        # Get content type of incoming request
        content_type = self.headers.get("Content-Type")
        # Get length of data content
        content_length = int(self.headers.get("Content-Length"))
        # Read entire binary data
        data = self.rfile.read(content_length)
        # Write data into a jpeg file
        with open("img.jpeg", "wb") as img:
            img.write(data)
        # Call UI tools function to run image processing module
        present_menu()
        # Send response
        self.send_response(200)
        self.end_headers()
        self.wfile.write("POST Request received".encode())


# Runs http server on specified port
def run(server_class=HTTPServer, handler_class=HTTPRequestHandler):
    server_address = ('', PORT)
    # Constructs server, specifying address and handler
    httpd = server_class(server_address, handler_class)
    # Start the server (polls for requests at regular intervals)
    httpd.serve_forever()


if __name__ == '__main__':
    run()
