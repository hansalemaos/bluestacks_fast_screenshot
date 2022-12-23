import subprocess
from ctypes_screenshots import screencapture_window
import cv2
import time
import pandas as pd
from a_cv2_easy_resize import add_easy_resize_to_cv2
from time import time
from ctypes_window_info import get_window_infos

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
    hwnd=None,
    interpolation=cv2.INTER_AREA,
    ignore_exceptions=True,
    show_fps=True,
):
    connect_to_adb(adb_path, deviceserial)
    screenadbx, screenadby = get_screenwidth(adb_path, deviceserial)
    if hwnd is None:
        from a_pandas_ex_automate_win32 import find_elements

        df = pd.DataFrame(find_elements())

        filter1 = df.loc[df.title.str.contains(windowtitle)]
        if filter1.empty:
            filter1 = df.loc[df.windowtext.str.contains(windowtitle)]

        possible_proc = df.loc[df.pid.isin(filter1.pid)]
        filter1 = possible_proc.loc[
            possible_proc.title.str.contains(
                "BlueStacks Keymap Overlay", na=False, regex=False
            )
        ]

        if filter1.empty:
            filter1 = df.loc[
                df.windowtext.str.contains(
                    "BlueStacks Keymap Overlay", na=False, regex=False
                )
            ]

        right_proc = df.loc[df.pid.isin(filter1.pid)]
        lf = right_proc.loc[right_proc.title.str.contains(windowtitle)]
        if lf.empty:
            lf = right_proc.loc[right_proc.windowtext.str.contains(windowtitle)]

        hwnd = int(lf.hwnd.iloc[0])
    print(f"hWnd: {hwnd}")

    ita = screencapture_window(hwnd)
    loop_time = None
    while True:
        try:
            if show_fps:
                loop_time = time()
            df = pd.DataFrame(get_window_infos())
            ctypescreen = next(ita)
            fi1x = df.loc[df.hwnd == hwnd]
            pid = fi1x.pid.iloc[0]
            alleb = df.loc[df.pid == pid]
            locas = alleb.loc[
                (
                    alleb.title.str.contains(
                        "BlueStacks Keymap Overlay", na=False, regex=False
                    )
                )
                | (
                    alleb.windowtext.str.contains(
                        "BlueStacks Keymap Overlay", na=False, regex=False
                    )
                )
                | (
                    alleb.class_name.str.contains(
                        "BlueStacks Keymap Overlay", na=False, regex=False
                    )
                )
            ]
            x, y = locas.dim_client.iloc[0]
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
            continue
