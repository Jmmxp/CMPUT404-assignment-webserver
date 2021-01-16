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


class MyWebServer(socketserver.BaseRequestHandler):
    def get_file(self):
        data_split = self.data.decode("utf-8").split(" ")
        method, req_file = data_split[0], data_split[1]
        print(method, req_file)

        if method != "GET":
            self.send_bytes("HTTP/1.1 405 Method Not Allowed\n")

        if req_file == "/":
            return "/index.html"

        return req_file

    def send_bytes(self, string):
        self.request.sendall(bytearray(string, "utf-8"))

    def content_type(self, req_file):
        content_type = ""
        if req_file.endswith("html"):
            content_type = "text/html"
        elif req_file.endswith("css"):
            content_type = "text/css"
        else:
            raise FileNotFoundError("File not found.")
        return content_type

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        req_file = self.get_file()

        try:
            with open("www" + req_file, "r") as index_file:
                index = index_file.read()
                self.send_bytes("HTTP/1.1 200 OK\n")
                self.send_bytes("Content-Type: " + self.content_type(req_file) + "\n")

                # This newline marks the end of the HTTP response headers.
                self.send_bytes("\n")
                self.send_bytes(index)
        except FileNotFoundError as e:
            print("File not found")
            self.send_bytes("HTTP/1.1 404 Not Found\n")


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
