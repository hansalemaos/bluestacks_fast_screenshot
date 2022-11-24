### This module takes screenshots of BlueStacks using the win32 API, resizes and crops them to the same size of an ADB screenshot.  

##### You can easily get more than 100 FPS, but the BlueStacks window may not be minimized! You can put it in the background, but don't minimize it!
##### Once you have called calculate_crop(), you can move the BlueStacks window, but don't resize it! 


```python
pip install bluestacks-fast-screenshot


from bluestacks_fast_screenshot import BluestacksScreencapWin32
import re
import cv2

bluestacksfast = BluestacksScreencapWin32(
    deviceserial="localhost:5735",
    adb_path="C:\\Users\\Gamer\\AppData\\Local\\Android\\Sdk\\platform-tools\\adb.exe",
    hwnd=None,
    window_text=re.compile(r".*bluestacks.*", flags=re.IGNORECASE),
    show_capture_keys="ctrl+alt+z",  # starts cv2.imshow() - can be enabled/disabled by pressing ctrl+alt+z
    show_fps_keys="ctrl+alt+f",  # show the fps rate - can be enabled/disabled by pressing ctrl+alt+f
    kill_screencap_keys="ctrl+alt+x",  # kills the capture process
)


for pic in bluestacksfast.calculate_crop(
    mincrop=15,  # Limit the crop size here, but be careful, if the value is too high, the picture will not be cropped properly
    maxcrop=70,  # Limit the crop size here, but be careful, if the value is too low, the picture will not be cropped properly
    interpolation=cv2.INTER_AREA,
).get_converted_screenshots(
    interpolation=cv2.INTER_AREA, sleeptime=None, force_cropcoords_update=False
):
    # print('do something here', end='\r')
    print(pic.shape, end="\r")
bluestacksfast.kill_screencap()  # if you break out of the loop, stop capturing

```

