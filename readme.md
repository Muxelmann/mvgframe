# MVGframe

A project to interface an [ESP8266](https://www.waveshare.com/wiki/E-Paper_ESP8266_Driver_Board) with a 7.5inch e-Paper display ([black-and-white](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT), [black-white-red](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_(B)) or [black-white-yellow](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_(C))) by Waveshare for displaying a [MVG](https://www.mvg.de/) (Munich public transport) timetable.

Run by calling

```sh
python3 main.py
```

## API overivew

The following commands can be called via HTTP (e.g. a browser) to set up the screens connected to the server.

### Setting functions

The following functions manipulate what will be displayed on the screens and how.

```
192.168.x.x:8080/setScreenInfo.api
```

Pass MAC address and two integers as GET parameters ```macAddress```, ```width``` and ```height``` to set the screen size.


```
192.168.x.x:8080/setScreenColor.api
```

Pass MAC address and one integer as GET parameters  ```macAddress``` and ```isColor```, wherein ```1``` is color and ```0``` is black and white.

```
192.168.x.x:8080/setFrameInfo.api
```

Pass MAC address and four integer as GET parameters  ```macAddress```, ```xOffset```, ```yOffset```, ```width``` and ```height```, to adjust how far the actually visible part of the visible frame is offset (x and y as pixels) and how large the visible frame is (w and h as pixels).

```
192.168.x.x:8080/setStation.api
```

Pass MAC address, one string and (optionally) a list of line filters as GET parameters  ```macAddress```, ```stationName``` and ```labelFilter``` (last parameter is optional), to store the station or bus stop for which departures are to be displayed - e.g. "Ehrengutstrasse" or "Arabellapark". If you are interested in a single line departing from this destination pass the line number/s as filter - e.g. "132,186" or "132," (with trailing comma)

### Getting functions

The following functions are called by the screens. You may also call them for debugging purposes.

```
192.168.x.x:8080/updateData.api
```

Pass MAC address as GET parameter to update the image (i.e. BMP) that will be displayed on the screen.

```
192.168.x.x:8080/getBmpData.api
```

Pass MAC address and two (optional) integers as GET parameters ```segmentsCount``` and ```segmentNumber``` to get the BMP pixel data (optionally) in horizontal segments. Here the ```segmentsCount``` remains constant (e.g. 4) and the ```segmentNumber``` is changed for each call (e.g. 0, 1, 2, 3) to gradually obtain the whole BMP data. This is used since the frame (ESP) has a limited input buffer size.

```
192.168.x.x:8080/getDelayTime.api
```

Pass MAC address as GET parameter to obtain the duration (in ms) the frame (ESP) will wait before updating.

```
192.168.x.x:8080/willReceiveColorData.api
```

Pass MAC address as GET parameter to obtain information as to whether the screen has been set to color (returns 1) or black and white (returns 0).


## TODO

- [ ] Handle URL encoding to allow German characters (*üöäß*) and space as station names
- [ ] Compute better delay time instead of always returning 30s (i.e. 30000ms) fixed delay
- [ ] Write website to allow easier settings/interface with API
- [ ] Display BMP on website
