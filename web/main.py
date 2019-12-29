from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver, time, os, urllib.parse

from apiHandler import ApiHandler
from interfaceHandler import InterfaceHandler

PORT_NUMBER = 8080

class ESPServerHandler(BaseHTTPRequestHandler):
    # Handler for the GET requests
    def do_GET(self):
        self.protocol_version = "HTTP/1.1"
        reply_content = ""
        reply_type = ""

        # separate GET args
        if "?" in self.path:
            self.path, getArgs = self.path.split("?", 1)
            if getArgs is None:
                getArgs = {}
            else:
                keys = [a.split("=")[0] for a in getArgs.split("&")]
                vals = [a.split("=")[1] for a in getArgs.split("&")]
                getArgs = dict(zip(keys, vals))
        else:
            getArgs = {}
        
        
        # test if api query
        if self.path.endswith(".api"):

            apiHandler = ApiHandler()
            apiHandler.setApiFunction(self.path.split(".")[0][1:])
            apiHandler.setApiArgs(getArgs)
            reply_content = apiHandler.getReplyContent()
            reply_type = "text/html"
            reply_code = 200
        
        # otherwise interface query
        else:
            interfaceHandler = InterfaceHandler()
            interfaceHandler.setInterfaceResource(self.path)
            interfaceHandler.setInterfaceArgs(getArgs)
            reply_content = interfaceHandler.getReplyContent()
            reply_type = interfaceHandler.getReplyType()
            reply_code = interfaceHandler.getReplyCode()

        # respond with reply content
        self.send_response(reply_code)
        self.send_header("Content-type", reply_type)
        self.send_header("Content-Length","{}".format(len(reply_content)))
        self.end_headers()
        if isinstance(reply_content, str):
            self.wfile.write(reply_content.encode("utf-8"))
        else:
            self.wfile.write(reply_content)
        return


try:
    server = HTTPServer(("", PORT_NUMBER), ESPServerHandler)
    print("Started server for mvgframe on port {}".format(PORT_NUMBER))

    server.serve_forever()

except KeyboardInterrupt:
    print("^C received, shutting down the web server")
    server.socket.close()

