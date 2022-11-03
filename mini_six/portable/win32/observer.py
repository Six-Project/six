# -*- coding:utf-8 -*-
"""

@Auther: niu
@FileName: observer.py
@Introduction: 定义 Observer 类

"""
from __future__ import annotations

from ctypes import byref, c_ubyte

import numpy as np

import mini_six.core as core
from mini_six.portable.win32.windll import (
    GetDC,
    CreateCompatibleDC,
    GetClientRect,
    CreateCompatibleBitmap,
    SetProcessDPIAware,
    SelectObject,
    BitBlt,
    GetBitmapBits,
    DeleteObject,
    ReleaseDC,
    RECT,
    SRCCOPY,
)

__all__ = ["ScreenshotObserver"]

SetProcessDPIAware()


@core.Agent.register()
class ScreenshotObserver(core.Observer):
    """
    适配 windows 窗口截图
    """

    def __init__(self, device_id):
        super().__init__(device_id)

        r = RECT()
        GetClientRect(device_id, byref(r))
        self._width, self._height = r.right, r.bottom
        self._frame = bytearray(self._width * self._height * 4)

        self._dc = GetDC(device_id)
        self._cdc = CreateCompatibleDC(self._dc)

    def __del__(self):
        DeleteObject(self._cdc)
        ReleaseDC(self.device_id, self._dc)

    def run(self):
        total_bytes = len(self._frame)
        bitmap = CreateCompatibleBitmap(self._dc, self._width, self._height)
        SelectObject(self._cdc, bitmap)
        BitBlt(self._cdc, 0, 0, self._width, self._height, self._dc, 0, 0, SRCCOPY)
        byte_array = c_ubyte * total_bytes
        GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(self._frame))
        DeleteObject(bitmap)
        image = np.frombuffer(self._frame, dtype=np.uint8).reshape(self._height, self._width, 4)
        self.agent.notify(self, image)
