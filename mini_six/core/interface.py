# -*- coding:utf-8 -*-
"""

@Auther: niu
@FileName: interface.py
@Introduction: 

"""
from __future__ import annotations

from mini_six.core.config import Config
import mini_six.core.abstract as abstract


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

__all__ = ["Agent", "Observer", "DataSourceType", "SubscribeData"]

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





class Agent(metaclass=abstract.SingleMeta):

    def __init__(self):
        self._subscribe_dict: Dict[int, SubscribeControlBlock] = {}

    def subscribe(self, source_type_dict: Dict[DataSourceType, _Observer], device_id_iter: Union[int, Iterable[int]]):
        """
        1. ?????? device_id ?????? subscribe ??????
        2. ?????? device_id ?????????????????? observer
        3. ?????? device_id ?????????????????????????????????????????????
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
    ?????? Observer ???????????????????????????????????????????????????????????????????????????????????????
    ?????? agent ??? notify ??????, ?????? oid ???????????????????????????
    """

    def __init__(self, device_id: int):
        """
        device_id?????????????????????/??????
        period????????????????????? period ms / ??????
        """
        self.device_id = device_id

    def pull(self, *args, **kwargs):
        """
        ?????? Observer ???????????????
        """
        raise NotImplementedError("????????? pull ?????????")


class Observer(_Observer):

    def pull(self, *args, **kwargs):
        raise NotImplementedError("????????? pull ?????????")


@dataclass
class SubscribeControlBlock:
    device_id: int
    observers: Dict[DataSourceType, _Observer]
    actions: List[Action]


@dataclass(order=True)
class Action:
    priority: int
    call: Callable = field(compare=False)
