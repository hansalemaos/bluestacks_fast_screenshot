import subprocess
from ctypes_screenshots import screencapture_window
import cv2
import time
from ctypes_window_info import get_window_infos
import pandas as pd
from a_cv2_easy_resize import add_easy_resize_to_cv2
from time import time

add_easy_resize_to_cv2()


def cropimage(img, coords):
    return img[coords[1] : coords[3], coords[0] : coords[2]].copy()


def get_screenwidth(adb_path, deviceserial):
    screenwidth, screenheight = (
        subprocess.run(
            rf'{adb_path} -s {deviceserial} shell dumpsys window | grep cur= |tr -s " " | cut -d " " -f 4|cut -d "=" -f 2',
            shell=True,
            capture_output=True,
        )
        .stdout.decode("utf-8", "ignore")
        .strip()
        .split("x")
    )
    screenwidth, screenheight = int(screenwidth), int(screenheight)
    return screenwidth, screenheight


def connect_to_adb(adb_path, deviceserial):
    _ = subprocess.run(f"{adb_path} start-server", capture_output=True, shell=False)
    _ = subprocess.run(
        f"{adb_path} connect {deviceserial}", capture_output=True, shell=False
    )


def get_bluestacks_screenshot(
    adb_path,
    deviceserial,
    windowtitle,
    interpolation=cv2.INTER_AREA,
    ignore_exceptions=True,
    show_fps=True,
):

    connect_to_adb(adb_path, deviceserial)
    screenadbx, screenadby = get_screenwidth(adb_path, deviceserial)
    df = pd.DataFrame(get_window_infos())
    filter1 = df.loc[df.title.str.contains(windowtitle)]
    possible_proc = df.loc[df.pid.isin(filter1.pid)]
    filter1 = possible_proc.loc[
        possible_proc.title.str.contains("BlueStacks Keymap Overlay")
    ]
    right_proc = df.loc[df.pid.isin(filter1.pid)]
    hwnd = int(right_proc.loc[right_proc.title.str.contains(windowtitle)].hwnd.iloc[0])
    ita = screencapture_window(hwnd)
    loop_time = None
    while True:
        try:
            if show_fps:
                loop_time = time()
            df = pd.DataFrame(get_window_infos())
            ctypescreen = next(ita)
            x, y = (
                df.loc[df.pid == df.loc[df.hwnd == hwnd].pid.iloc[0]].iloc[0].dim_client
            )
            croppedim = cropimage(
                ctypescreen, (1, ctypescreen.shape[0] - y, x, ctypescreen.shape[0])
            )
            yield cv2.easy_resize_image(
                croppedim,
                width=screenadbx,
                height=screenadby,  # pic2.shape[0] + mincrop,
                percent=None,
                interpolation=interpolation,
            )
            if show_fps:
                print("FPS {}            ".format(1 / (time() - loop_time)), end="\r")

        except Exception as fe:
            if not ignore_exceptions:
                raise fe
