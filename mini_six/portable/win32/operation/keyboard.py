# -*- coding:utf-8 -*-
"""

@Auther: niu
@FileName: keyboard.py
@Introduction: 定义了模拟键盘按键的基础操作

"""
from typing import Iterable

from mini_six.portable.win32.windll import PostMessageW, WM_KEYDOWN, WM_KEYUP, KEY_MAP

__all__ = ["press_key", "release_key", "click_key", "click_combination_key"]


def press_key(handle, char: str):
    """
    按下一个键盘按键
    """
    wparam = KEY_MAP[char]
    lparam = None
    PostMessageW(handle, WM_KEYDOWN, wparam, lparam)


def release_key(handle, char: str):
    """
    松开一个键盘按键
    """
    wparam = KEY_MAP[char]
    lparam = None
    PostMessageW(handle, WM_KEYUP, wparam, lparam)


def click_key(handle, char: str):
    """
    单击一个键盘按键
    """
    press_key(handle, char)
    release_key(handle, char)


def click_combination_key(handle, char_iter: Iterable[str]):
    """
    单击键盘组合按键
    """
    for char in char_iter:
        press_key(handle, char)
    for char in char_iter:
        release_key(handle, char)
