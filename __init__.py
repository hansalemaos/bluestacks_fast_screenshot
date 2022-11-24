import ctypes
import subprocess
from time import sleep, time
from typing import Union
import pandas as pd
from skimage.feature import match_template
import numpy as np
from a_cv_imwrite_imread_plus import add_imwrite_plus_imread_plus_to_cv2

add_imwrite_plus_imread_plus_to_cv2()
from window_capture_streaming import WindowIterCapture
import re
from adb_screencap_streaming import ADBScreenshot
import cv2
from a_cv2_easy_resize import add_easy_resize_to_cv2

add_easy_resize_to_cv2()
import keyboard as keyboardxx___


def connect_to_adb(adb_path, deviceserial):
    _ = subprocess.run(f"{adb_path} start-server", capture_output=True, shell=False)
    _ = subprocess.run(
        f"{adb_path} connect {deviceserial}", capture_output=True, shell=False
    )


def cropimage(img, coords):
    return img[coords[1] : coords[3], coords[0] : coords[2]].copy()


def getting_index_of_max_value_in_dataframe(df):
    return np.unravel_index(np.argmax(df, axis=None), df.shape)


def get_screenwidth(adb_path, deviceserial):
    screenwidth, screenheight = (
        subprocess.run(
            fr'{adb_path} -s {deviceserial} shell dumpsys window | grep cur= |tr -s " " | cut -d " " -f 4|cut -d "=" -f 2',
            shell=True,
            capture_output=True,
        )
        .stdout.decode("utf-8", "ignore")
        .strip()
        .split("x")
    )
    screenwidth, screenheight = int(screenwidth), int(screenheight)
    return screenwidth, screenheight


def get_window_rectangle(hwnd) -> tuple:
    rect = ctypes.wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hex(hwnd), ctypes.pointer(rect))
    return rect.left, rect.top, rect.right, rect.bottom


class BluestacksScreencapWin32:
    def __init__(
        self,
        deviceserial: str,
        adb_path: str,
        hwnd: Union[None, int] = None,
        window_text: Union[None, re.Pattern, str] = None,
        show_capture_keys: str = "ctrl+alt+z",
        show_fps_keys: str = "ctrl+alt+f",
        kill_screencap_keys: str = "ctrl+alt+x",
    ):
        self.deviceserial = deviceserial
        self.adb_path = adb_path
        if hwnd is None and window_text is not None:
            hwnd = WindowIterCapture.find_window_with_regex(window_text)
        self.window_text = window_text
        self.hwnd = hwnd
        print(self.hwnd)
        self.window_rect = get_window_rectangle(self.hwnd)
        self.w = self.window_rect[2] - self.window_rect[0]
        self.h = self.window_rect[3] - self.window_rect[1]
        self.offset_x = self.window_rect[0]
        self.offset_y = self.window_rect[1]
        self.df = pd.DataFrame()
        self.stop = False

        self.show_capture_keys = show_capture_keys
        self.show_capture = False
        keyboardxx___.add_hotkey(self.show_capture_keys, self._show_capture_switch)
        self.show_fps_keys = show_fps_keys
        self.show_fps = False
        keyboardxx___.add_hotkey(self.show_fps_keys, self._show_fps_keys_switch)
        self.popenpid = None
        self.kill_screencap_keys = kill_screencap_keys
        keyboardxx___.add_hotkey(self.kill_screencap_keys, self.kill_screencap)
        self.width_height = None
        self.cropcoords = None
        self.is_smaller_than_original = False
        self.maxcrop = None
        self.mincrop = None
        self.adb_dimensions = None

    def _show_capture_switch(self):
        self.show_capture = not self.show_capture

    def _show_fps_keys_switch(self):
        self.show_fps = not self.show_fps

    def kill_screencap(self):
        print("Killing ...")
        self.show_fps = False
        self.show_capture = False
        sleep(1)
        self.stop = True
        sleep(1)
        cv2.destroyAllWindows()

    def calculate_crop(
        self, mincrop: int = 15, maxcrop: int = 30, interpolation: int = cv2.INTER_AREA
    ):
        self.maxcrop = maxcrop
        self.mincrop = mincrop
        adb_path = self.adb_path
        deviceserial = self.deviceserial
        hwnd = self.hwnd
        window_text = self.window_text

        def get_crop_values():

            connect_to_adb(adb_path=adb_path, deviceserial=deviceserial)
            screenwidth, screenheight = get_screenwidth(
                adb_path=adb_path, deviceserial=deviceserial
            )

            capt = WindowIterCapture(
                hwnd=hwnd,
                window_text=window_text,
                show_capture_keys="ctrl+alt+z+k+i+m+t+q",
                show_fps_keys="ctrl+alt+f+k+i+m+t+q",
                kill_screencap_keys="ctrl+alt+x+k+i+m+t+q",
            )
            allscreenshots_win = []
            for screen_shot in capt.get_screenshot(
                sleeptime=None,
                resize_width=screenwidth + maxcrop,
                resize_height=screenheight + maxcrop,
                resize_percent=None,
                interpolation=interpolation,
            ):
                try:
                    allscreenshots_win.append(screen_shot.copy())
                    if len(allscreenshots_win) >= 1:
                        break
                except Exception:
                    continue
            capt.kill_screencap()

            allscreenshots_adb = []
            bilder = ADBScreenshot(
                adb_path=adb_path,
                deviceserial=deviceserial,
                show_capture_keys="ctrl+alt+z+k+i+m+t+q",
                show_fps_keys="ctrl+alt+f+k+i+m+t+q",
                kill_screencap_keys="ctrl+alt+x+k+i+m+t+q",
            )
            for ka in bilder.get_adb_screenshots(
                sleeptime=None,
                resize_width=None,
                resize_height=None,
                resize_percent=None,
                interpolation=interpolation,
            ):
                try:
                    allscreenshots_adb.append(ka.copy())
                    if len(allscreenshots_adb) >= 1:
                        break
                except Exception:
                    continue
            bilder.kill_screencap()
            adb_dimensions = (
                allscreenshots_adb[0].shape[1],
                allscreenshots_adb[0].shape[0],
            )
            pic1 = cv2.imread_plus(allscreenshots_win[0], channels_in_output=2)
            pic2 = cv2.imread_plus(allscreenshots_adb[0], channels_in_output=2)
            is_smaller_than_original = False
            if pic1.shape[0] <= pic2.shape[0]:
                is_smaller_than_original = True
                pic1 = cv2.imread_plus(
                    cv2.easy_resize_image(
                        allscreenshots_win[0].copy(),
                        width=pic2.shape[1] + mincrop,
                        height=None,  # pic2.shape[0] + mincrop,
                        percent=None,
                        interpolation=interpolation,
                    ),
                    channels_in_output=2,
                )

            all_best_values = []
            for _ in range(pic1.shape[0] - pic2.shape[0]):
                newdim = pic1.shape[1] - _, pic1.shape[0] - _
                print(f"Checking: {newdim}", end="\r")

                pic3 = cv2.easy_resize_image(
                    pic1.copy(),
                    width=newdim[0],
                    height=newdim[1],
                    percent=None,
                    interpolation=interpolation,
                )
                reas = match_template(pic3, pic2)
                df = pd.concat(
                    [pd.DataFrame(x) for x in reas], axis=1, ignore_index=True
                )
                all_best_values.append((df.copy(), newdim, pic3.shape))
                if pic3.shape[0] - pic2.shape[0] <= mincrop:
                    break

            together = []
            for df, newdim, shape in all_best_values:
                maxwert = df.max().max()
                for col in df.columns:
                    dfe = df.loc[df[col] == maxwert]
                    if not dfe.empty:
                        together.append((maxwert, dfe.index[0], col, newdim, shape))

            dfn = pd.DataFrame(together)
            bestvalue = dfn.sort_values(by=0, ascending=False).iloc[0].to_list()
            newshapeofcapturedwindow = bestvalue[-2]
            crop_start_x = bestvalue[1]
            crop_start_y = bestvalue[2]
            crop_end_x = pic2.shape[1] + crop_start_x
            crop_end_y = pic2.shape[0] + crop_start_y
            return (
                newshapeofcapturedwindow,
                (crop_start_x, crop_start_y, crop_end_x, crop_end_y),
                adb_dimensions,
                is_smaller_than_original,
            )

        (
            width_height,
            cropcoords,
            adb_dimensions,
            is_smaller_than_original,
        ) = get_crop_values()
        self.width_height = width_height
        self.cropcoords = cropcoords
        self.adb_dimensions = adb_dimensions
        self.is_smaller_than_original = is_smaller_than_original
        return self

    def get_converted_screenshots(
        self,
        interpolation: int = cv2.INTER_AREA,
        sleeptime: Union[None, float, int] = None,
        force_cropcoords_update: bool = False,
    ) -> np.ndarray:
        hwnd = self.hwnd
        window_text = self.window_text

        capt = WindowIterCapture(
            hwnd=hwnd,
            window_text=window_text,
            show_capture_keys="ctrl+alt+shift+a+b+c+d+e+f+g+i",
            show_fps_keys="ctrl+alt+shift+a+b+c+d+e+f+g+h",
            kill_screencap_keys="ctrl+alt+shift+a+b+c+d+e+f+g",
        )
        if (
            self.width_height is None
            or self.cropcoords is None
            or force_cropcoords_update is True
        ):
            self.calculate_crop()
        width_height = self.width_height
        cropcoords = self.cropcoords
        self.stop = False
        cv2.destroyAllWindows()
        sleep(0.5)
        loop_time = time()
        killcvwindow = False
        resize_width = width_height[0]
        # resize_height = width_height[1]

        if self.is_smaller_than_original:
            resize_width = self.adb_dimensions[0] + self.mincrop
            # resize_height = self.adb_dimensions[1].shape[0] + self.mincrop
        try:
            for screen_shot in capt.get_screenshot(
                sleeptime=None,
                resize_width=resize_width,
                resize_height=None,
                resize_percent=None,
                interpolation=interpolation,
            ):

                try:
                    if self.stop:
                        break
                    img = cropimage(
                        cv2.imread_plus(screen_shot, channels_in_output=3), cropcoords
                    )
                    yield img
                    if self.show_fps:
                        print(
                            "FPS {}            ".format(1 / (time() - loop_time)),
                            end="\r",
                        )
                    if self.show_capture:
                        killcvwindow = True
                        cv2.imshow(fr"picture", img)
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            cv2.destroyAllWindows()
                    else:
                        if killcvwindow:
                            cv2.destroyAllWindows()
                        killcvwindow = False
                    if sleeptime is not None:
                        sleep(sleeptime)
                    loop_time = time()
                except Exception:
                    continue
                except KeyboardInterrupt:
                    try:
                        try:
                            self.kill_screencap()
                        except:
                            pass
                        break
                    except Exception:
                        break

        except KeyboardInterrupt:
            pass
        try:
            self.kill_screencap()
        except:
            pass
        try:
            capt.kill_screencap()
        except:
            pass


