# -*- coding:utf-8 -*-
"""

@Auther: niu
@FileName: mouse.py
@Introduction: 定义模拟鼠标点击的基本操作

"""
__all__ = ["move_to", "left_down", "left_up", "scroll_up", "scroll_down", "scroll", "left_click"]

from typing import Union

import mini_six.portable.win32.windll as windll


def move_to(handle: windll.HWND, x: int, y: int):
    """移动鼠标到坐标（x, y)

    Args:
        handle (HWND): 窗口句柄
        x (int): 横坐标
        y (int): 纵坐标
    """
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-mousemove
    wparam = 0
    lparam = y << 16 | x
    windll.PostMessageW(handle, windll.WM_MOUSEMOVE, wparam, lparam)


def left_down(handle: windll.HWND, x: int, y: int):
    """在坐标(x, y)按下鼠标左键

    Args:
        handle (HWND): 窗口句柄
        x (int): 横坐标
        y (int): 纵坐标
    """
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-lbuttondown
    wparam = 0
    lparam = y << 16 | x
    windll.PostMessageW(handle, windll.WM_LBUTTONDOWN, wparam, lparam)


def left_up(handle: windll.HWND, x: int, y: int):
    """在坐标(x, y)放开鼠标左键

    Args:
        handle (HWND): 窗口句柄
        x (int): 横坐标
        y (int): 纵坐标
    """
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-lbuttonup
    wparam = 0
    lparam = y << 16 | x
    windll.PostMessageW(handle, windll.WM_LBUTTONUP, wparam, lparam)


def scroll(handle: windll.HWND, delta: int, x: int, y: int):
    """在坐标(x, y)滚动鼠标滚轮

    Args:
        handle (HWND): 窗口句柄
        delta (int): 为正向上滚动，为负向下滚动
        x (int): 横坐标
        y (int): 纵坐标
    """
    move_to(handle, x, y)
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-mousewheel
    wparam = delta << 16
    p = windll.POINT(x, y)
    windll.ClientToScreen(handle, windll.byref(p))
    lparam = p.y << 16 | p.x
    windll.PostMessageW(handle, windll.WM_MOUSEWHEEL, wparam, lparam)


def scroll_up(handle: windll.HWND, x: int, y: int):
    """在坐标(x, y)向上滚动鼠标滚轮

    Args:
        handle (HWND): 窗口句柄
        x (int): 横坐标
        y (int): 纵坐标
    """
    scroll(handle, windll.WHEEL_DELTA, x, y)


def scroll_down(handle: windll.HWND, x: int, y: int):
    """在坐标(x, y)向下滚动鼠标滚轮

    Args:
        handle (HWND): 窗口句柄
        x (int): 横坐标
        y (int): 纵坐标
    """
    scroll(handle, -windll.WHEEL_DELTA, x, y)


def left_click(handle: Union[int, windll.HWND], x: int, y: int):
    left_down(handle, x, y)
    left_up(handle, x, y)
