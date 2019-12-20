from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import urllib.parse
from datetime import datetime
import pickle, time

from PIL import Image, ImageFont, ImageDraw 
import os, sys

import mvg_api

PORT_NUMBER = 8080

# Update functions
def updateData(macAddress, screen):
    # screen properties
    xOffset = screen["frame"]["xOffset"]
    yOffset = screen["frame"]["yOffset"]
    stationName = screen["station"]["name"]
    stationFilter = screen["station"]["filter"]

    station_id = mvg_api.get_id_for_station(stationName)
    departures = mvg_api.get_departures(station_id)
    for i in range(len(departures)):
        departures[i]["destination"] = " ".join([d for d in departures[i]["destination"].split(" ") if len(d) > 1])

    img = Image.new("1", (screen["screen"]["width"], screen["screen"]["height"]))
    draw = ImageDraw.Draw(img)
    draw.rectangle([
        xOffset,
        yOffset,
        screen["frame"]["xOffset"] + screen["frame"]["width"],
        screen["frame"]["yOffset"] + screen["frame"]["height"]], fill="white")
    
    xOffset += 25
    yOffset += 7

    font_site = 42
    fonts_path = os.path.join(os.path.dirname(__file__), 'fonts')
    font = ImageFont.truetype(os.path.join(fonts_path, 'EXCITE.otf'), font_site)
    font_bold = ImageFont.truetype(os.path.join(fonts_path, 'EXCITE_B.otf'), font_site)

    max_departures = 7
    i = 0
    for departure in departures:
        if i >= max_departures:
            break

        # if a filter is set, only display what is in filter
        if len(stationFilter) > 0 and departure["label"] not in stationFilter:
            continue

        # continue if departure has been canceled
        if departure["cancelled"]:
            continue

        # get the delay and add to the (planned) departure time
        delay_time = departure["delay"] * 60 if "delay" in departure.keys() else 0
        departure_time = departure["departureTime"] / 1000

        departure_time_str = datetime.fromtimestamp(delay_time + departure_time).strftime("%H:%M")
        draw.text((xOffset, yOffset + font_site*1.1*i), departure_time_str, 0, font=font_bold)
        departure_destination = departure["destination"]
        draw.text((xOffset+130, yOffset+font_site*1.1*i), departure_destination, 0, font=font)
        i += 1

    if len(departures) == 0:
        draw.text((xOffset, yOffset), "Nachtruhe", 0, font=font)

    img.save(macAddress.replace(":", "") + "-departures.bmp")

def getBmpData(macAddress, segCount, segNumber):
    img_path = macAddress.replace(":", "") + "-departures.bmp"
    image = Image.open(img_path)
    image = image.rotate(180)
    (width, height) = image.size
    box = (0, height / segCount * (segNumber), width, height / segCount * (segNumber+1))
    image = image.crop(box)
    (width, height) = image.size
    
    vals = ""
    px = image.load()
    for y in range(height):
        for x in range(0, width, 8):
            digits = ['0', '1']
            val = [int(px[x+i, y]/255) for i in range(8)]
            val = int("".join([ digits[y] for y in val ]), 2)
            vals += "{:02x}".format(val)
    return vals

def getBmpDataColor(macAddress, segCount, segNumber):
    img_path = macAddress.replace(":", "") + "-departuresColor.bmp"
    image = Image.open(img_path)
    image = image.rotate(180)
    (width, height) = image.size
    box = (0, height / segCount * (segNumber), width, height / segCount * (segNumber+1))
    image = image.crop(box)
    (width, height) = image.size
    
    vals = ""
    px = image.load()
    for y in range(height):
        for x in range(0, width, 8):
            digits = ['0', '1']
            val = [int(px[x+i, y]/255) for i in range(8)]
            val = int("".join([ digits[y] for y in val ]), 2)
            vals += "{:02x}".format(val)
    return vals

class ScreenHandler():

    def __init__(self):
        self._screens_file = "screens.pkl"
        if not os.path.exists(self._screens_file):
            self._saveScreens({})

    def _loadScreens(self):
        f = open(self._screens_file, "rb")
        screens = pickle.load(f)
        f.close()
        return screens

    def _loadScreensWithMacAddress(self, macAddress):
        screens = self._loadScreens()
        if macAddress not in screens.keys():
            screens[macAddress] = {
                "screen": {"width": 640, "height": 384, "color": False},
                "frame": {"xOffset": 50, "yOffset": 5, "width": 544, "height": 349},
                "station" : {"name": "Ehrengutstrasse", "filter" : []}
                }
            self._saveScreens(screens)
        return screens

    def _saveScreens(self, screens):
        f = open(self._screens_file, "wb")
        pickle.dump(screens, f)
        f.close()

    def setScreenInfo(self, macAddress, width, height):
        screens = self._loadScreensWithMacAddress(macAddress)
        
        screens[macAddress]["screen"]["width"] = int(width)
        screens[macAddress]["screen"]["height"] = int(height)

        self._saveScreens(screens)

    def setScreenColor(self, macAddress, isColor):
        screens = self._loadScreensWithMacAddress(macAddress)

        screens[macAddress]["screen"]["color"] = isColor

        self._saveScreens(screens)

    def isScreenColor(self, macAddress):
        screens = self._loadScreensWithMacAddress(macAddress)
        return screens[macAddress]["screen"]["color"]

    def setFrameInfo(self, macAddress, xOffset, yOffset, width, height):
        screens = self._loadScreensWithMacAddress(macAddress)
        
        screens[macAddress]["frame"]["xOffset"] = int(xOffset)
        screens[macAddress]["frame"]["yOffset"] = int(yOffset)
        screens[macAddress]["frame"]["width"] = int(width)
        screens[macAddress]["frame"]["height"] = int(height)

        self._saveScreens(screens)

    def setStation(self, macAddress, stationName, labelFilter=[]):
        screens = self._loadScreensWithMacAddress(macAddress)

        screens[macAddress]["station"]["name"] = stationName
        screens[macAddress]["station"]["filter"] = labelFilter

        self._saveScreens(screens)

    def getScreenForMacAddress(self, macAddress):
        screens = self._loadScreensWithMacAddress(macAddress)
        return screens[macAddress]

class ESPServerHandler(BaseHTTPRequestHandler):
    # Handler for the GET requests
    def do_GET(self):
        self.protocol_version = "HTTP/1.1"
        reply_content = ""

        # separate GET args
        if "?" in self.path:
            self.path, self.get_args = self.path.split("?", 1)
            if self.get_args is None:
                self.get_args = {}
            else:
                keys = [a.split("=")[0] for a in self.get_args.split("&")]
                vals = [a.split("=")[1] for a in self.get_args.split("&")]
                self.get_args = dict(zip(keys, vals))
        else:
            self.get_args = {}
        
        if "." in self.path:
            self.call_function = self.path.split(".")[0][1:]

        # test if api query
        if self.path.endswith(".api"):
            self.send_response(200)
            
            screens = ScreenHandler()
            # Setup functions
            if self.call_function == "setScreenInfo":
                screens.setScreenInfo(self.get_args["macAddress"], self.get_args["width"], self.get_args["height"])
                reply_content += "1"
            if self.call_function == "setScreenColor":
                screens.setScreenColor(self.get_args["macAddress"], int(self.get_args["isColor"]) > 0)
                reply_content += "screen set to color (BRW)" if int(self.get_args["isColor"]) > 0 else "screen set to black and white"
            elif self.call_function == "setFrameInfo":
                screens.setFrameInfo(self.get_args["macAddress"], self.get_args["xOffset"], self.get_args["yOffset"], self.get_args["width"], self.get_args["height"])
                reply_content += "1"
            elif self.call_function == "setStation":
                if "labelFilter" in self.get_args.keys():
                    screens.setStation(self.get_args["macAddress"], self.get_args["stationName"], self.get_args["labelFilter"].split(","))
                else:
                    screens.setStation(self.get_args["macAddress"], self.get_args["stationName"])


            # Update functions
            elif self.call_function == "updateData":
                screen = screens.getScreenForMacAddress(self.get_args["macAddress"])
                updateData(self.get_args["macAddress"], screen)
                reply_content = "1"
            elif self.call_function == "getBmpData":
                self.get_args["segmentsCount"] = self.get_args["segmentsCount"] if "segmentsCount" in self.get_args.keys() else "1"
                self.get_args["segmentNumber"] = self.get_args["segmentNumber"] if "segmentNumber" in self.get_args.keys() else "0"
                if screens.isScreenColor(self.get_args["macAddress"]):
                    reply_content += getBmpDataColor(self.get_args["macAddress"], int(self.get_args["segmentsCount"]), int(self.get_args["segmentNumber"]))
                else:
                    reply_content += getBmpData(self.get_args["macAddress"], int(self.get_args["segmentsCount"]), int(self.get_args["segmentNumber"]))
            elif self.call_function == "getDelayTime":
                reply_content += "30000"
            elif self.call_function == "willReceiveColorData":
                reply_content += "1" if screens.isScreenColor(self.get_args["macAddress"]) else "0"
            else:
                print("unknown function")
        
        else:
        
            # Error message
            self.send_response(404)
            reply_content += "404 page not found"


        self.send_header("Content-type","text/html")
        self.send_header("Content-Length","{}".format(len(reply_content)))
        self.end_headers()
        self.wfile.write(reply_content.encode("utf-8"))
        return


try:
    server = HTTPServer(("", PORT_NUMBER), ESPServerHandler)
    print("Started server for mvgframe on port {}".format(PORT_NUMBER))

    server.serve_forever()

except KeyboardInterrupt:
    print("^C received, shutting down the web server")
    server.socket.close()

