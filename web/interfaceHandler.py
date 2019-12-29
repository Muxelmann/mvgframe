from screenData import ScreenData
import os, pprint

class InterfaceHandler(object):

    def setInterfaceResource(self, interfaceResource):
        self._interfaceResource = interfaceResource[1:] if len(interfaceResource[1:]) > 0 else "interface.html"
        if not os.path.exists(self._interfaceResource):
            self._interfaceResource = "interface/" + self._interfaceResource

    def setInterfaceArgs(self, interfaceArgs):
        self._interfaceArgs = interfaceArgs

    def getReplyContent(self):
        print(self._interfaceResource)
        resourceSuffix = self._interfaceResource.split(".")[-1] if len(self._interfaceResource.split(".")) > 1 else "html"

        if not os.path.exists(self._interfaceResource):
            self._replyCode = 404
            self._replyType = "text/html"
            f = open("interface/404.html", "rb")
            data = f.read()
            f.close()
            print("404 ({})".format(self._interfaceResource))
            return data
        else:
            self._replyCode = 200

        f = open(self._interfaceResource, "rb")
        data = f.read()
        f.close()

        if resourceSuffix in ["html", "css", "js"]:
            self._replyType = "text/" + resourceSuffix + "; charset=utf-8"
            data = data.decode("utf-8")
            
            if resourceSuffix == "html":
                return self._formatData(data)
            else:
                return data

        if resourceSuffix in ["png", "jpg", "bmp"]:
            self._replyType = "image/" + resourceSuffix
            return data

        # special suffixes
        mimeDict = {
            "map": "application/json",
            "ttf": "application/octet-stream",
            "woff": "font/woff",
            "woff2": "font/woff2"
        }
        if resourceSuffix in mimeDict.keys():
            self._replyType = mimeDict[resourceSuffix]
            return data


        print("unknown file: {}".format(self._interfaceResource))
        return ""

    def getReplyType(self):
        return self._replyType

    def getReplyCode(self):
        return 200

    def _formatData(self, data):

        screens = ScreenData().getAllScreens()
        macAddress = self._interfaceArgs["macAddress"] if "macAddress" in self._interfaceArgs.keys() else None
        
        if "<!--#SCREENS_CODE#-->" in data:
            pre = "<pre>" + pprint.pformat(screens) + "<pre>"
            data = data.replace("<!--#SCREENS_CODE#-->", pre)
        
        if "<!--#SCREEN_DATA#-->" in data:

            if macAddress:
                f = open("interface/_screen-card.html", "r")
                screenData = f.read()
                f.close()

                screenData = screenData.replace("<!--#MAC_ADDRESS#-->", macAddress)
                screenData = screenData.replace("<!--#SCREEN_CODE-->", pprint.pformat(screens[macAddress]))
                screenData = screenData.replace("<!--#SCREEN_IMAGE#-->", "../../" + macAddress.replace(":", "") + "-departures.bmp")
                data = data.replace("<!--#SCREEN_DATA#-->", screenData)
            else:
                data = data.replace("<!--#SCREEN_DATA#-->", "Chose")

        if "<!--#SCREEN_LIST#-->" in data:
            f = open("interface/_sidebar-entry.html", "r")
            sidebarEntry = f.read()
            f.close()

            replacementText = ""
            for macAddressEntry in screens.keys():
                if macAddress and macAddress == macAddressEntry:
                    replacementText += sidebarEntry.replace("<!--#MAC_ADDRESS#-->", macAddressEntry).replace("<!--#IS_MAC_ADDRESS_SELECTED#-->", "active")
                else:
                    replacementText += sidebarEntry.replace("<!--#MAC_ADDRESS#-->", macAddressEntry).replace("<!--#IS_MAC_ADDRESS_SELECTED#-->", "")

            data = data.replace("<!--#SCREEN_LIST#-->", replacementText)
        return data