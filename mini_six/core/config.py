# -*- coding:utf-8 -*-
"""

@Auther: niu
@FileName: config.py
@Introduction: 负责管理全局和局部的环境变量配置

"""
import mini_six.core.abstract as abstract
import os
import json
from collections import deque

GLOBAL_CONFIG = {
    "clock": 0.1,
    "env_fp": "env.json",
    "debug": False
}


class Config(metaclass=abstract.SingleMeta):
    """
    配置项的名称一律使用小写字母存储
    """

     # 插件调用栈

    def __init__(self):
        self._config = {}
        self._env_stack = deque()
        self._push("global")
        self._load_static_config()

    def _load_static_config(self):
        current_layer = self._env_stack[0]

        if current_layer != "global":
            raise ValueError("Unexpected error.")

        self._config[current_layer].update(GLOBAL_CONFIG)

        env_json_fp = self._config[current_layer]["env_fp"]

        if os.path.exists(env_json_fp):
            with open(env_json_fp, "r", encoding="utf-8") as fr:
                global_static_env = json.load(fr)

            self._config[current_layer].update(global_static_env)

    def _push(self, env_layer):
        self._env_stack.appendleft(env_layer)
        if env_layer not in self._config:
            self._config[env_layer] = {}

    def _pop(self):
        item = self._env_stack.popleft()
        return item

    def add(self, env_items: dict):
        """在当前空间设置新的环境变量"""

        current_layer = self._env_stack[0]
        config = self._config.get(current_layer, None)

        if config is None:
            raise ValueError(f"Unexpected value: current_layer={current_layer}.")

        config.update(env_items)

    def get(self, variable):
        """获取当前空间已定义的环境变量值，若当前空间无，则获取全局环境变量"""

        current_layer = self._env_stack[0]

        config = self._config.get(current_layer, None)

        if config is None:
            raise ValueError(f"Unexpected value: current_layer={current_layer}.")

        value = self._config[current_layer].get(variable, None)

        if value is None:
            value = self._config["global"].get(variable, None)
            if value is None:
                raise KeyError(f"Can't find variable {variable} in {current_layer} space.")

        return value
