# -*- coding:utf-8 -*-
"""

@Auther: niu
@FileName: windll.py
@Introduction: 定义了 windll 库函数的调用接口

"""

import ctypes

from ctypes import windll
from ctypes import wintypes

__all__ = ["RECT", "byref", "c_ubyte", "HWND", "POINT", "GetDC", "CreateCompatibleDC", "GetClientRect",
           "CreateCompatibleBitmap", "SetProcessDPIAware", "SelectObject", "BitBlt", "GetBitmapBits",
           "DeleteObject", "ReleaseDC", "PostMessageW", "ClientToScreen", "SRCCOPY", "SendMessageW", "WM_MOUSEMOVE",
           "WM_ACTIVATE", "WM_LBUTTONUP", "WM_LBUTTONDOWN", "WM_MOUSEWHEEL", "WHEEL_DELTA", "WM_KEYUP", "WM_KEYDOWN",
           "KEY_MAP"]

# types
RECT = wintypes.RECT
byref = ctypes.byref
c_ubyte = ctypes.c_ubyte
HWND = wintypes.HWND
POINT = wintypes.POINT

# function
GetDC = windll.user32.GetDC
CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
GetClientRect = windll.user32.GetClientRect
CreateCompatibleBitmap = windll.gdi32.CreateCompatibleBitmap
SetProcessDPIAware = windll.user32.SetProcessDPIAware
SelectObject = windll.gdi32.SelectObject
BitBlt = windll.gdi32.BitBlt
GetBitmapBits = windll.gdi32.GetBitmapBits
DeleteObject = windll.gdi32.DeleteObject
ReleaseDC = windll.user32.ReleaseDC
PostMessageW = windll.user32.PostMessageW
SendMessageW = windll.user32.SendMessageW
ClientToScreen = windll.user32.ClientToScreen

SRCCOPY = 0x00CC0020

WM_ACTIVATE = 0x0006
# Mouse
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x202
WM_MOUSEWHEEL = 0x020A
WHEEL_DELTA = 120

# Keyboard
WM_KEYUP = 0x0101
WM_KEYDOWN = 0x0100
KEY_MAP = {
    "\0": 0x20,
}
