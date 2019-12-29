import os, sys, pickle

class ScreenData():

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
                "station" : {"name": "Ehrengutstraße,München", "filter" : []}
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

    def setStation(self, macAddress, stationName, labelFilter):
        screens = self._loadScreensWithMacAddress(macAddress)

        screens[macAddress]["station"]["name"] = stationName
        screens[macAddress]["station"]["filter"] = labelFilter

        self._saveScreens(screens)

    def getScreenForMacAddress(self, macAddress):
        screens = self._loadScreensWithMacAddress(macAddress)
        return screens[macAddress]

    def getAllScreens(self):
        return self._loadScreens()