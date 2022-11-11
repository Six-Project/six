# -*- coding:utf-8 -*-
"""

@Auther: niu
@FileName: keyboard.py
@Introduction: 定义了模拟键盘按键的基础操作

"""
from typing import Iterable

from mini_six.portable.win32.windll import PostMessageW, WM_KEYDOWN, WM_KEYUP, KEY_MAP

__all__ = ["press_key", "release_key", "click_key", "click_combination_key"]


def press_key(handle, key: int):
    """
    按下一个键盘按键
    """
    wparam = key
    lparam = None
    PostMessageW(handle, WM_KEYDOWN, wparam, lparam)


def release_key(handle, key: int):
    """
    松开一个键盘按键
    """
    wparam = key
    lparam = None
    PostMessageW(handle, WM_KEYUP, wparam, lparam)


def click_key(handle, key: int):
    """
    单击一个键盘按键
    """
    press_key(handle, key)
    release_key(handle, key)


def click_combination_key(handle, key_iter: Iterable[int]):
    """
    单击键盘组合按键
    """
    for key in key_iter:
        press_key(handle, key)
    for key in key_iter:
        release_key(handle, key)
