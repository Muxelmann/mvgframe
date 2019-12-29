from datetime import datetime
from PIL import Image, ImageFont, ImageDraw 
import os

from screenData import ScreenData
import mvg_api

# Update functions
def updateData(macAddress, screen):
    # screen properties
    xOffset = screen["frame"]["xOffset"]
    yOffset = screen["frame"]["yOffset"]
    stationName = screen["station"]["name"]
    stationFilter = screen["station"]["filter"]

    station_id = mvg_api.get_id_for_station(stationName)
    departures = mvg_api.get_departures(station_id)

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
    departures_display = []
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
        departure_delay = departure["delay"] * 60.0 if "delay" in departure.keys() else 0.0
        departure_time = departure["departureTime"] / 1000.0
        departure_destination = " ".join([d for d in departure["destination"].split(" ") if len(d) > 1])

        # Removing the "U" and "S" from the end of the destination
        departures_display.append([departure_time, departure_delay, departure_destination])
        i += 1

    departures_display.sort(key=lambda x: x[0] + x[1])
    i = 0
    for departure in departures_display:
        departure_time_str = datetime.fromtimestamp(departure[0] + departure[1]).strftime("%H:%M")
        draw.text((xOffset, yOffset + font_site*1.1*i), departure_time_str, 0, font=font_bold)
        draw.text((xOffset+130, yOffset+font_site*1.1*i), departure[2], 0, font=font)
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

class ApiHandler(object):
    
    def setApiFunction(self, apiFunction):
        self._apiFunction = apiFunction

    def setApiArgs(self, apiArgs):
        self._apiArgs = apiArgs

    def getReplyContent(self):
        screens = ScreenData()

        if "macAddress" not in self._apiArgs.keys():
            print("No MAC address passed")
            return ""
        else:
            macAddress = self._apiArgs["macAddress"]

        # Setup functions
        if self._apiFunction == "setScreenInfo":
            if not all(x in self._apiArgs.keys() for x in ["width", "height"]):
                print("setScreenInfo requires args: width and height")
                return "0"

            width = self._apiArgs["width"]
            height = self._apiArgs["height"]
            screens.setScreenInfo(macAddress, width, height)
            return "1"

        if self._apiFunction == "setScreenColor":
            if not all(x in self._apiArgs.keys() for x in ["isColor"]):
                print("setScreenColor requires arg: isColor")
                return "0"
            
            isColor = int(self._apiArgs["isColor"]) > 0
            screens.setScreenColor(macAddress, isColor)
            return "screen set to color (BRW)" if isColor else "screen set to black and white"

        if self._apiFunction == "setFrameInfo":
            if not all(x in self._apiArgs.keys() for x in ["xOffset", "yOffset", "width", "height"]):
                print("setFrameInfo requires args: xOffset, yOffset, width and height")
                return "0"

            xOffset = self._apiArgs["xOffset"]
            yOffset = self._apiArgs["yOffset"]
            width = self._apiArgs["width"]
            height = self._apiArgs["height"]
            screens.setFrameInfo(macAddress, xOffset, yOffset, width, height)
            return "1"

        if self._apiFunction == "setStation":
            if not all(x in self._apiArgs.keys() for x in ["stationName"]):
                print("setStation requires args: stationName and (optionally) labelFilter")
                return "0"
            
            stationName = self._apiArgs["stationName"]
            labelFilter = self._apiArgs["labelFilter"].split(",") if "labelFilter" in self._apiArgs.keys() else []
            screens.setStation(macAddress, stationName, labelFilter)
            return "1"


        # Update functions
        if self._apiFunction == "updateData":
            screen = screens.getScreenForMacAddress(macAddress)
            updateData(macAddress, screen)
            return "1"
        
        if self._apiFunction == "getBmpData":
            self._apiArgs["segmentsCount"] = self._apiArgs["segmentsCount"] if "segmentsCount" in self._apiArgs.keys() else "1"
            self._apiArgs["segmentNumber"] = self._apiArgs["segmentNumber"] if "segmentNumber" in self._apiArgs.keys() else "0"
            if screens.isScreenColor(macAddress):
                return getBmpDataColor(macAddress, int(self._apiArgs["segmentsCount"]), int(self._apiArgs["segmentNumber"]))
            else:
                return getBmpData(macAddress, int(self._apiArgs["segmentsCount"]), int(self._apiArgs["segmentNumber"]))
        
        if self._apiFunction == "getDelayTime":
            return "30000"
        
        if self._apiFunction == "willReceiveColorData":
            return "1" if screens.isScreenColor(macAddress) else "0"
        
        print("unknown function: {}".format(self._apiFunction))
        return ""