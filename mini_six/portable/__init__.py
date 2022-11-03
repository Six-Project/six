# -*- coding:utf-8 -*-
"""

@Auther: niu
@FileName: __init__.py.py
@Introduction: 

"""
import sys

__all__ = ["observer", "operation"]

if sys.platform == "win32":
    import mini_six.portable.win32.observer as observer
    import mini_six.portable.win32.operation as operation
