#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

class MethodNotAllowedError(Exception):
    """
    Error representing that a provided HTTP method (e.g., POST) is not supported. 
    """
    pass

class MyWebServer(socketserver.BaseRequestHandler):
    def get_file(self):
        """
        From a GET request, return the file name that is requested.
        
        Raises MethodNotAllowedError if the request was not a GET request.
        Raises FileNotFoundError if the request cannot be parsed properly. 
        """
        data_split = self.data.decode("utf-8").split(" ")
        if len(data_split) < 2:
            raise FileNotFoundError("Request cannot be parsed properly - file not found.")

        method, req_file = data_split[0], data_split[1]

        if method != "GET":
            raise MethodNotAllowedError("HTTP method " + method + " is not allowed.")

        if req_file.endswith("/"):
            return req_file + "index.html"

        return req_file

    def host(self):
        """ 
        Returns the "Host" header value from the request.

        Code by StackOverflow user Liam Kelly https://stackoverflow.com/u/1987437
        https://stackoverflow.com/a/39090882
        """
        fields = self.data.decode("utf-8").split("\r\n")
        fields = fields[1:] # ignore the first line of the request
        output = {}
        for field in fields:
            if not field:
                continue
            key, value = field.split(": ") # split each line by http field name and value
            output[key] = value.strip()

        return output["Host"]

    def content_type(self, req_file):
        """
        Get the content type of the requested file. Only supports text/html and text/css.
        
        Raises FileNotFoundError if the file is a mimetype other than text/html and text/css. 
        """
        content_type = ""
        if req_file.endswith("html"):
            content_type = "text/html"
        elif req_file.endswith("css"):
            content_type = "text/css"
        else:
            raise FileNotFoundError("File not found.")
        return content_type

    def send_bytes(self, string):
        """
        Encodes the string into a bytearray and sends it in a response back to the client. 
        """
        self.request.sendall(bytearray(string, "utf-8"))

    def handle(self):
        """
        Handles an HTTP GET request. 
        
        Fetches the html/css file that is requested in the GET and returns it to the client.

        If a file that does not exist on the server, or is not html/css is requested, 
        404 Not Found is returned.

        If the requested file is a directory, 301 Permanently Moved is returned, 
        with the corrected resource in the Location response header.

        IF the HTTP request contained a method other than GET, 405 Method Not Allowed 
        is returned.
        """
        self.data = self.request.recv(1024).strip()

        try:
            req_file = self.get_file()

            with open("www" + req_file, "r") as index_file:
                index = index_file.read()
                content_type = self.content_type(req_file)

                # Code by StackOverflow user falsetru https://stackoverflow.com/u/2225682 
                # https://stackoverflow.com/a/21153368
                self.send_bytes("HTTP/1.1 200 OK\r\n")
                self.send_bytes("Content-Type: " + content_type + "\r\n")

                # This newline marks the end of the HTTP response headers.
                self.send_bytes("\r\n")
                self.send_bytes(index)
        except FileNotFoundError:
            self.send_bytes("HTTP/1.1 404 Not Found\r\n")
        except IsADirectoryError:
            self.send_bytes("HTTP/1.1 301 Moved Permanently\r\n")
            self.send_bytes(f"Location: http://{self.host()}{req_file}/\r\n")
        except MethodNotAllowedError:
            self.send_bytes("HTTP/1.1 405 Method Not Allowed\r\n")

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
