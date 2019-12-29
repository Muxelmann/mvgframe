from screenData import ScreenData
import os, pprint

class InterfaceHandler(object):

    def setInterfaceResource(self, interfaceResource):
        self._interfaceResource = interfaceResource[1:] if len(interfaceResource[1:]) > 0 else "interface.html"
        self._interfaceResource = "interface/" + self._interfaceResource

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
            
            if "<!--#SCREEN_DATA#-->" in data:
                screens = ScreenData().getAllScreens()
                pre = "<pre>" + pprint.pformat(screens) + "<pre>"
                data = data.replace("<!--#SCREEN_DATA#-->", pre)
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