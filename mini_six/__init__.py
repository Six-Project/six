# -*- coding:utf-8 -*-
"""

@Auther: niu
@FileName: __init__.py.py
@Introduction: 

"""
from mini_six.core import Config  # 加载 Config
from mini_six.core import Agent  # 加载 Agent
from mini_six.core import DataSource
import mini_six.logger  # 加载 log 配置
import mini_six.portable as portable

__all__ = ["watch", "operation", "init", "load_plugin", "run"]

agent = Agent()
watch = agent.watch
operation = portable.operation
KEYMAP = portable.key_map


def init():
    agent.init()


def load_plugin(plugin_dir, plugin_name):
    """
    通过文件路径加载插件
    :return:
    """
    agent.load_plugin(plugin_dir, plugin_name)


def run():
    agent.run()
