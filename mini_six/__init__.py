# -*- coding:utf-8 -*-
"""

@Auther: niu
@FileName: __init__.py.py
@Introduction: 

"""
from mini_six.core import Config  # 加载 Config
from mini_six.core import Agent  # 加载 Agent
import mini_six.logger  # 加载 log 配置
import mini_six.portable as portable

from mini_six.core import DataSourceType
from mini_six.core import SubscribeData

__all__ = ["subscribe", "operation", "DataSourceType", "SubscribeData", "Config"]

agent = Agent()
subscribe = agent.subscribe
operation = portable.operation
KEYMAP = portable.key_map


def load_plugin(plugin_dir, plugin_name):
    """
    通过文件路径加载插件
    :return:
    """
    load_plugin(plugin_dir, plugin_name)


def run():
    agent.run()
