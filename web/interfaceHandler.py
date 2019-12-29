from screenData import ScreenData
import os, pprint

class InterfaceHandler(object):

    def setInterfaceResource(self, interfaceResource):
        self._interfaceResource = interfaceResource[1:] if len(interfaceResource[1:]) > 0 else "interface.html"

    def getReplyContent(self):
        print(self._interfaceResource)
        interfaceType = self._interfaceResource.split(".")[1] if len(self._interfaceResource.split(".")) > 1 else "html"

        if not os.path.exists(self._interfaceResource):
            self._replyCode = 404
            self._replyType = "text/html"
            return "404 Page not found"
        else:
            self._replyCode = 200

        f = open(self._interfaceResource, "rb")
        data = f.read()
        f.close()

        if interfaceType == "html":
            self._replyType = "text/html; charset=utf-8"
            data = data.decode("utf-8")
            
            if "<!--#SCREEN_DATA#-->" in data:
                screens = ScreenData().getAllScreens()
                pre = "<pre>" + pprint.pformat(screens) + "<pre>"
                data = data.replace("<!--#SCREEN_DATA#-->", pre)
            return data

        if interfaceType in ["png", "jpg", "bmp"]:
            self._replyType = "image/" + interfaceType
            return data

    def getReplyType(self):
        return self._replyType

    def getReplyCode(self):
        return 200