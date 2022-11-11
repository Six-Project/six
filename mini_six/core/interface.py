# -*- coding:utf-8 -*-
"""

@Auther: niu
@FileName: interface.py
@Introduction: 

"""
from __future__ import annotations

from mini_six.core.config import Config
import mini_six.core.abstract as abstract

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
from typing import Dict, Callable, List, Union, Iterable, Type

__all__ = ["Agent", "Observer", "DataSource", "SubscribeMode"]

config = Config()
logger = logging.getLogger("six")


class SubscribeMode(enum.Enum):
    PULL = 0
    PUSH = 1


class DataSourceType(enum.Enum):
    IMAGE = 0


class DataSource(enum.Enum):
    SCREENSHOT = DataSourceType.IMAGE


@dataclass
class Image:
    data: np.ndarray
    handle: int


class ObserverRunningEvent(threading.Event):
    """该事件控制 Observer 线程的运行"""
    pass


class Agent(metaclass=abstract.SingleMeta):
    _observer_running_event = ObserverRunningEvent()

    def __init__(self):
        self._observer_factory_map: Dict[DataSource, Type[_Observer]] = dict()

        # device_id 与 ocb 具有一对一映射关系
        self._device_to_ocb_map: Dict[int, ObserverControlBlock] = dict()
        # 第三方 ocb 映射表：(device_id, observer_class_name) 与 ocb 具有一对一映射关系
        self._device_to_ocb_map_t: Dict[tuple[int, str], ObserverControlBlock] = dict()

        # push action
        # device_id 与 acb 具有一对多映射关系
        self._push_device_to_acb_map: Dict[int, List[ActionControlBlock]] = dict()
        # 第三方 acb 映射表：(device_id, observer_class_name) 与 acb 具有一对多映射关系
        self._push_device_to_acb_map_t: Dict[tuple[int, str], List[ActionControlBlock]] = dict()

        # pull action
        self._scheduler = sched.scheduler()
        # device_id 与 acb 具有一对多映射关系
        self._pull_device_to_acb_map: Dict[int, List[ActionControlBlock]] = dict()
        # 第三方 acb 映射表：(device_id, observer_class_name) 与 acb 具有一对多映射关系
        self._pull_device_to_acb_map_t: Dict[tuple[int, str], List[ActionControlBlock]] = dict()

    def init(self):
        """
        慢加载内置模块：Agent 必须早于 Observer 加载完
        """
        import mini_six.portable as portable
        self._observer_factory_map[DataSource.SCREENSHOT] = portable.observer.ScreenshotObserver
        logger.info("@start-up Builtin observers load successfully.")

    def load_plugin(self, plugin_dir, plugin_name):
        """
        按路径加载第三方模块
        """
        sys.path.append(plugin_dir)
        config._push(plugin_name)
        importlib.import_module(plugin_name)
        config._pop()
        sys.path.remove(plugin_dir)

        logger.info(f"@start-up Plugin [{plugin_name}] load successfully.")

    def look(self, source_type: DataSource, device_id_iter: Union[int, Iterable[int]], period=1, priority=1,
             subscribe_mode=SubscribeMode.PUSH):
        """通过 device_id 注册一个 visual observer，可取的值见类属性 DataSource """

        if source_type not in DataSource:
            raise ValueError(f"Unexpected value source_type={source_type}.")

        if source_type.value != DataSourceType.IMAGE:
            raise TypeError(f"Watch function doesn't support {source_type}.")

        obs_factory = self._observer_factory_map[source_type]

        if subscribe_mode == SubscribeMode.PUSH:
            device_to_acb_map = self._push_device_to_acb_map
        elif subscribe_mode == SubscribeMode.PULL:
            device_to_acb_map = self._pull_device_to_acb_map
        else:
            raise ValueError(f"Unexpected value subscribe_mode={subscribe_mode}.")

        if not isinstance(device_id_iter, Iterable):
            device_id_iter = [device_id_iter]

        def _decorator(func):
            inner_func = func

            for device_id in device_id_iter:
                if device_id not in self._device_to_ocb_map:
                    obs = obs_factory(device_id)
                    obs.agent = self
                    ocb = ObserverControlBlock(
                        device_id=device_id, observer=obs,
                    )
                    self._device_to_ocb_map[device_id] = ocb

                    device_to_acb_map[device_id] = []

                    logger.info("@start-up Builtin observer instance "
                                f"[{type(ocb.observer).__name__}-{device_id}] is created successfully.")
                else:
                    ocb = self._device_to_ocb_map[device_id]

                if subscribe_mode == SubscribeMode.PULL:
                    @functools.wraps(func)
                    def inner_func():
                        data = obs.pull()
                        image = Image(data=data, handle=device_id)
                        res = func(image)
                        logger.info(
                            f"@act-done Action [{acb.function.__name__}] react to "
                            f"[{type(obs).__name__}-{obs.device_id}] successfully.")
                        delay = ocb.observer.period * period * config.get("clock")
                        self._scheduler.enter(delay, priority, inner_func)
                        return res

                acb = ActionControlBlock(function=inner_func, subordinate_plugin=config._env_stack[0],
                                         datasource_type=DataSourceType.IMAGE, period=period, priority=priority,
                                         subscribe_mode=subscribe_mode)
                device_to_acb_map[device_id].append(acb)

                logger.info(
                    f"@start-up Action [{inner_func.__name__}] subscribe to "
                    f"[{type(ocb.observer).__name__}-{device_id}] successfully.")
            return inner_func

        return _decorator

    def look_t(self, t_source: Type[Observer], device_id_iter: Union[int, Iterable[int]], period=1):
        tmp_obs = t_source(0)

        if not isinstance(tmp_obs, Observer):
            raise ValueError(f"Unexpected value t_source={t_source}.")

        if not isinstance(device_id_iter, Iterable):
            device_id_iter = [device_id_iter]

        obs_cls_name = str(type(tmp_obs))

        def _decorator(func):
            for device_id in device_id_iter:
                if (device_id, obs_cls_name) not in self._device_to_ocb_map_t:
                    obs = t_source(device_id)
                    obs.agent = self
                    ocb = ObserverControlBlock(
                        device_id=device_id, observer=obs,
                    )
                    self._device_to_ocb_map_t[(device_id, obs_cls_name)] = ocb
                    self._push_device_to_acb_map_t[(device_id, obs_cls_name)] = []

                    logger.info("@start-up Third-party observer instance "
                                f"[{type(ocb.observer).__name__}-{device_id}] is created successfully.")
                else:
                    ocb = self._device_to_ocb_map_t[(device_id, obs_cls_name)]

                acb = ActionControlBlock(function=func, subordinate_plugin=config._env_stack[0],
                                         datasource_type=DataSourceType.IMAGE, period=period)
                self._push_device_to_acb_map_t[(device_id, obs_cls_name)].append(acb)

                logger.info(
                    f"@start-up Action [{func.__name__}] subscribe to "
                    f"[{type(ocb.observer).__name__}-{device_id}] successfully.")
            return func

        return _decorator

    def notify(self, obs: Observer, data) -> None:
        """
        通知所有所有正在监听的 manual-zh-cn.md：同一个 Observer 下的 manual-zh-cn.md 是顺序执行的
        """
        logger.debug(f"@obs-update Observer [{obs.device_id}] update information.")

        if isinstance(obs, Observer):
            acb_list = self._push_device_to_acb_map_t[(obs.device_id, str(type(obs)))]
        elif isinstance(obs, _Observer):
            acb_list = self._push_device_to_acb_map[obs.device_id]
        else:
            raise ValueError(f"Unexpected value obs={str(type(obs))}.")

        for acb in acb_list:

            """
            为避免出现相除出现浮点数和舍入问题（保证相对精确性），此处 acb 的计时基准
            为全局时钟周期（下称时间周期）：假设 observer 每观测一次耗费 n 个时间周
            期，则 acb 的 clock_count 加 n，直到等于 period 时，方可执行。
            """
            acb.clock_count += obs.period
            if acb.clock_count >= acb.period:
                acb.clock_count = 0

                try:
                    config._push(acb.subordinate_plugin)

                    if acb.datasource_type == DataSourceType.IMAGE:
                        _d = Image(data=data, handle=obs.device_id)
                        acb.function(_d)

                    logger.info(
                        f"@act-done Action [{acb.function.__name__}] react to "
                        f"[{type(obs).__name__}-{obs.device_id}] successfully.")

                except Exception as e:
                    logger.exception("@act-error Action failed to react to "
                                     f"[{type(obs).__name__}-{obs.device_id}] {e}")
                finally:
                    config._pop()

    @classmethod
    def register(cls):
        """注册 Observer"""

        def _decorator(_obs_class):
            @functools.wraps(_obs_class)
            def _inner(*args, **kwargs):
                return _obs_class(*args, **kwargs)

            # 将 observer 的 push 方法为改写为受控型
            old_push = _obs_class.push

            def _push(obs: Observer):
                while cls._observer_running_event.is_set():
                    old_push(obs)
                    # Observer 每观察一次会休眠 period 个时钟周期
                    time.sleep(obs.period * config.get("clock"))

            _obs_class.push = _push

            return _inner

        return _decorator

    def run(self):
        self._observer_running_event.set()

        for device_id, acb_list in self._push_device_to_acb_map.items():
            ocb = self._device_to_ocb_map[device_id]
            t = threading.Thread(name=f"{type(ocb.observer).__name__}-{ocb.observer.device_id}",
                                 target=ocb.observer.push, daemon=ocb.daemon)
            t.start()
            ocb.observer_status = ObserverStatus.RUNNING
            logger.info(
                f"@start-up Builtin observer instance [{type(ocb.observer).__name__}-{device_id}] is working...")

        for (device_id, obs_cls_name), ocb in self._push_device_to_acb_map_t.items():
            ocb = self._device_to_ocb_map_t[(device_id, obs_cls_name)]
            t = threading.Thread(name=f"{obs_cls_name}-{device_id}",
                                 target=ocb.observer.push, daemon=ocb.daemon)
            t.start()
            ocb.observer_status = ObserverStatus.RUNNING
            logger.info(f"@start-up Third-party observer instance [{obs_cls_name}-{device_id}] is working...")

        for device_id, acb_list in self._pull_device_to_acb_map.items():
            ocb = self._device_to_ocb_map[device_id]
            for acb in acb_list:
                delay = ocb.observer.period * acb.period * config.get("clock")
                self._scheduler.enter(delay, acb.priority, acb.function)

        for (device_id, obs_cls_name), acb_list in self._pull_device_to_acb_map_t.items():
            ocb = self._device_to_ocb_map[(device_id, obs_cls_name)]
            for acb in acb_list:
                delay = ocb.observer.period * acb.period * config.get("clock")
                self._scheduler.enter(delay, acb.priority, acb.function)

        t = threading.Thread(name="scheduler", target=self._scheduler.run, daemon=True)
        t.start()
        logger.info(f"@start-up Scheduler is working...")

        while True:
            if config.get("debug"):
                time.sleep(1)
            else:
                ans = input("是否结束程序？(Y/N)\n")
                if ans.upper() == "Y":
                    break
        self._observer_running_event.clear()

        logger.info(f"@shutdown main thread shutdown successfully.")


class _Observer:
    """
    定义 Observer 的基类，该类负责将外部信息输入到本系统内部，当信息更新后，
    调用 agent 的 notify 进行, 同一 oid 只能创建一个实例。
    """

    def __init__(self, device_id: int, period: int = 1):
        """
        device_id：输入设备句柄/文件
        period：观察周期（每 period ms / 次）
        """
        self.device_id = device_id
        self.period = period
        self.agent = None

    def pull(self, *args, **kwargs):
        """
        定义 Observer 的拉取流程
        """
        raise NotImplementedError("请重载 pull 方法。")

    def push(self, *args, **kwargs) -> None:
        """
        定义 Observer 的推送流程
        """
        raise NotImplementedError("请重载 push 方法。")


class Observer(_Observer):

    def pull(self, *args, **kwargs):
        raise NotImplementedError("请重载 pull 方法。")

    def push(self, *args, **kwargs) -> None:
        raise NotImplementedError("请重载 pull 方法。")


class ObserverStatus(enum.Enum):
    CREATE = 0
    RUNNING = 1
    TERMINATE = 2


@dataclass
class ObserverControlBlock:
    device_id: int
    observer: _Observer
    observer_status: ObserverStatus = field(default=ObserverStatus.CREATE)
    daemon: bool = field(default=True)


@dataclass
class ActionControlBlock:
    function: Callable
    subordinate_plugin: str
    datasource_type: DataSourceType
    subscribe_mode: SubscribeMode = field(default=SubscribeMode.PUSH)
    priority: int = field(default=1)
    period: int = field(default=1)  # ms 作为单位
    clock_count: int = field(default=0)
    heavy: bool = field(default=False)
