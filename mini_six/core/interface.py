# -*- coding:utf-8 -*-
"""

@Auther: niu
@FileName: interface.py
@Introduction: 

"""
from __future__ import annotations

from mini_six.core.config import Config
import mini_six.core.abstract as abstract

import asyncio
import sys
import sched
import enum
import time
import logging
import importlib
import functools
import threading
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Callable, List, Union, Iterable

__all__ = ["Agent", "Observer", "DataSourceType", "SubscribeData", "load_plugin"]

config = Config()
logger = logging.getLogger("six")


class DataSourceType(enum.Enum):
    IMAGE = 0


@dataclass
class SubscribeData:
    handle: int
    image: np.ndarray


def publisher_executor_factory(scb: SubscribeControlBlock):
    scheduler = sched.scheduler()
    clock = config.get("clock")
    idle_priority = 100

    def idle_task():
        time.sleep(clock)
        scheduler.enter(delay=clock, priority=idle_priority, action=idle_task)

    def action_factory(action: Action):
        @functools.wraps(action.call)
        def inner():
            subscribe_data_dict = {"handle": scb.device_id}
            for data_source_type, obs in scb.observers.items():
                if data_source_type == DataSourceType.IMAGE:
                    image = obs.pull()
                    subscribe_data_dict["image"] = image
            data = SubscribeData(**subscribe_data_dict)
            action.call(data)
            scheduler.enter(delay=clock, priority=action.priority, action=inner)

        return inner

    def run():
        scheduler.enter(delay=clock, priority=idle_priority, action=idle_task)
        for action in scb.actions:
            wrapped_action = action_factory(action)
            scheduler.enter(delay=clock, priority=action.priority, action=wrapped_action)
        scheduler.run()

    return run


def load_plugin(plugin_dir, plugin_name):
    """
    按路径加载第三方模块
    """
    sys.path.append(plugin_dir)
    config._push(plugin_name)
    importlib.import_module(plugin_name)
    config._pop()
    sys.path.remove(plugin_dir)

    logger.info(f"@start-up Plugin [{plugin_name}] load successfully.")


class Agent(metaclass=abstract.SingleMeta):

    def __init__(self):
        self._subscribe_dict: Dict[int, SubscribeControlBlock] = {}

    def subscribe(self, source_type_dict: Dict[DataSourceType, _Observer], device_id_iter: Union[int, Iterable[int]]):
        """
        1. 一个 device_id 只能 subscribe 一次
        2. 一个 device_id 可以订阅多个 observer
        3. 一个 device_id 对应一个线程，一个独立的运行域
        """

        for source_type, obs_factory in source_type_dict.items():
            if source_type not in DataSourceType:
                raise ValueError(f"Unexpected value source_type={source_type}.")

            if not issubclass(obs_factory, _Observer):
                raise ValueError(f"Unexpected value observer={obs_factory}.")

        if not isinstance(device_id_iter, Iterable):
            device_id_iter = [device_id_iter]

        def data_source(priority=1):
            def _decorator(func):
                action = Action(priority=priority, call=func)
                for device_id in device_id_iter:
                    if device_id not in self._subscribe_dict:
                        observers = {}
                        actions = [action]
                        for source_type, obs_factory in source_type_dict.items():
                            obs = obs_factory(device_id)
                            observers[source_type] = obs
                            logger.info(f"@start-up [publisher-{device_id}] create successfully.")

                        scb = SubscribeControlBlock(
                            device_id=device_id, observers=observers, actions=actions
                        )

                        self._subscribe_dict[device_id] = scb
                    else:
                        scb = self._subscribe_dict[device_id]
                        scb.actions.append(action)

                    logger.info(
                        f"@start-up Coroutine action [{func.__name__}] subscribe to "
                        f"[publisher-{device_id}] successfully.")
                return func

            return _decorator

        return data_source

    def run(self):
        thread_list = []
        for device_id, scb in self._subscribe_dict.items():
            t = threading.Thread(name=f"publisher-{device_id}", target=publisher_executor_factory(scb), daemon=True)
            thread_list.append(t)
        for t in thread_list:
            t.start()
            logger.info(f"@start-up [{t.name}] is working...")
        for t in thread_list:
            t.join()
            logger.info(f"@shutdown [{t.name}] shutdown successfully.")
        logger.info(f"@shutdown main thread shutdown successfully.")


class _Observer:
    """
    定义 Observer 的基类，该类负责将外部信息输入到本系统内部，当信息更新后，
    调用 agent 的 notify 进行, 同一 oid 只能创建一个实例。
    """

    def __init__(self, device_id: int):
        """
        device_id：输入设备句柄/文件
        period：观察周期（每 period ms / 次）
        """
        self.device_id = device_id

    def pull(self, *args, **kwargs):
        """
        定义 Observer 的拉取流程
        """
        raise NotImplementedError("请重载 pull 方法。")


class Observer(_Observer):

    def pull(self, *args, **kwargs):
        raise NotImplementedError("请重载 pull 方法。")


@dataclass
class SubscribeControlBlock:
    device_id: int
    observers: Dict[DataSourceType, _Observer]
    actions: List[Action]


@dataclass(order=True)
class Action:
    priority: int
    call: Callable = field(compare=False)
