from http.server import HTTPServer, BaseHTTPRequestHandler
import os
from K_Means import K_Means
from k_means_utils import get_timestamp_str
import json
import time

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
    # path: /Users/ediwu/Desktop/img3.jpg
    def do_POST(self):
        print("Incoming POST request.")
        time.sleep(5)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        json_str = json.dumps("hello there.")
        self.wfile.write(json_str.encode())
        # self.wfile.write("POST Request received".encode())
        # # Get content type of incoming request
        # content_type = self.headers.get("Content-Type")
        # # Get length of data content
        # content_length = int(self.headers.get("Content-Length"))
        # # Read entire binary data
        # data = self.rfile.read(content_length)
        # # Write data into a jpeg file
        # FILE_NAME = "src_images/flowers.jpeg"
        # with open(FILE_NAME, "wb") as img:
        #     img.write(data)
        # ### Call UI tools function to run image processing module
        # ### present_menu()
        # # Instantiate K-Means object and run process
        # # DEFAULTS
        # project_name = "DEFAULT_PROJECT"
        # k_values = (6, 6, 1)
        # num_runs = 1
        # img_extension = ".jpeg"
        # palette_replace = True
        # resize_level = 100
        # file_path = os.path.join(os.getcwd(), FILE_NAME)
        # log_file_name = f"{get_timestamp_str()}__{project_name}_{str(num_runs)}x_{k_values[0]}"
        # # END DEFAULTS
        # k_means_process = K_Means(project_name, k_values, file_path, num_runs, log_file_name, img_extension,
        #                           palette_replace, resize_level)
        # partial_result_path = k_means_process.run()
        #
        # # Read from result image from path and return to user
        # result_image_path = os.path.join(os.getcwd(), partial_result_path)
        #
        # # Send response
        # self.send_response(200)
        # self.send_header('Content-Type', 'image/jpeg')
        # self.end_headers()
        # # self.wfile.write('okay'.encode())
        # with open(result_image_path, 'rb') as result_image:
        #     self.wfile.write(result_image.read())


# Runs http server on specified port
def run(server_class=HTTPServer, handler_class=HTTPRequestHandler):
    server_address = ('', PORT)
    # Constructs server, specifying address and handler
    httpd = server_class(server_address, handler_class)
    # Start the server (polls for requests at regular intervals)
    httpd.serve_forever()


if __name__ == '__main__':
    run()
