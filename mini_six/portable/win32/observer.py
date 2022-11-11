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
    SendMessageW,
    WM_ACTIVATE
)

__all__ = ["ScreenshotObserver"]

SetProcessDPIAware()


@core.Agent.register()
class ScreenshotObserver(core.interface._Observer):
    """
    适配 windows 窗口截图
    """

    def __init__(self, device_id):
        super().__init__(device_id)

        r = RECT()
        GetClientRect(device_id, byref(r))
        self._width, self._height = r.right, r.bottom

    def pull(self):
        _frame = bytearray(self._width * self._height * 4)
        _dc = GetDC(self.device_id)
        _cdc = CreateCompatibleDC(_dc)
        total_bytes = len(_frame)
        SendMessageW(self.device_id, WM_ACTIVATE, 1, 0)
        bitmap = CreateCompatibleBitmap(_dc, self._width, self._height)
        SelectObject(_cdc, bitmap)
        BitBlt(_cdc, 0, 0, self._width, self._height, _dc, 0, 0, SRCCOPY)
        byte_array = c_ubyte * total_bytes
        GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(_frame))
        DeleteObject(bitmap)
        image = np.frombuffer(_frame, dtype=np.uint8).reshape(self._height, self._width, 4)
        DeleteObject(_cdc)
        ReleaseDC(self.device_id, _dc)
        return image

    def push(self):
        image = self.pull()
        self.agent.notify(self, image)
