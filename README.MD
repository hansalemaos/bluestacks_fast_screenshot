### This module takes screenshots of BlueStacks using the win32 API, resizes and crops them to the same size of an ADB screenshot.  

##### You can easily get more than 100 FPS, but the BlueStacks window may not be minimized! You can put it in the background, but don't minimize it!


```python
pip install bluestacks-fast-screenshot

# Update 22/12/2022 - Less code / less dependencies 

from bluestacks_fast_screenshot import get_bluestacks_screenshot
import cv2
blueit = get_bluestacks_screenshot(
    adb_path="C:\\Users\\USERNAME\\AppData\\Local\\Android\\Sdk\\platform-tools\\adb.exe",
    deviceserial="localhost:5795",
    windowtitle="bluestacks",
    interpolation=cv2.INTER_AREA,
    ignore_exceptions=True,
    show_fps=True,
)

for pic in blueit:
    # do your stuff here
    cv2.imshow("", pic.copy())
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        cv2.destroyAllWindows()
        break


```

