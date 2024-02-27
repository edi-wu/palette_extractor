from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8000


class HTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print("Incoming GET request.")
        for header, value in self.headers.items():
            print(f"{header}: {value}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write("GET Request received".encode())

    def do_POST(self):
        print("Incoming POST request.")
        content_type = self.headers.get("Content-Type")
        if content_type.startswith('multipart/form-data'):
            print("Content-Type: multipart/form-data")
        self.send_response(200)
        self.end_headers()
        self.wfile.write("POST Request received".encode())


def run(server_class=HTTPServer, handler_class=HTTPRequestHandler):
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == '__main__':
    run()
