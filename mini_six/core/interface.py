# -*- coding:utf-8 -*-
"""

@Auther: niu
@FileName: interface.py
@Introduction: 

"""
from __future__ import annotations

import sys

from mini_six.core.config import Config
import mini_six.core.abstract as abstract

import enum
import time
import logging
import importlib
import functools
import threading
from dataclasses import dataclass, field
from typing import Dict, Callable, List, Union, Iterable

__all__ = ["Agent", "Observer", "DataSource"]

config = Config()
logger = logging.getLogger("six")


class DataSource(enum.Enum):
    SCREENSHOT = "watch"


class ObserverRunningEvent(threading.Event):
    """该事件控制 Observer 线程的运行"""
    pass


class Agent(metaclass=abstract.SingleMeta):
    _observer_running_event = ObserverRunningEvent()

    def __init__(self):
        self._observer_factory_map = dict()

        # device_id 与 ocb 具有一对一映射关系
        self._device_to_ocb_map: Dict[int, ObserverControlBlock] = dict()

        # device_id 与 acb 具有一对多映射关系
        self._device_to_acb_map: Dict[int, List[ActionControlBlock]] = dict()

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

    def watch(self, source_type: DataSource, device_id_iter: Union[int, Iterable[int]], period=1):
        """通过 device_id 注册一个 visual observer，可取的值见类属性 DataSource """

        if source_type not in DataSource:
            raise ValueError(f"Unexpected value source_type={source_type}.")

        if source_type.value != "watch":
            raise TypeError(f"{source_type} should use {source_type.value} function.")

        if not isinstance(device_id_iter, Iterable):
            device_id_iter = [device_id_iter]

        def _decorator(func):
            for device_id in device_id_iter:
                if device_id not in self._device_to_ocb_map:
                    obs_factory = self._observer_factory_map[source_type]
                    obs = obs_factory(device_id)
                    obs.agent = self
                    ocb = ObserverControlBlock(
                        device_id=device_id, observer=obs,
                    )
                    self._device_to_ocb_map[device_id] = ocb
                    self._device_to_acb_map[device_id] = []

                    logger.info("@start-up Observer instance "
                                f"[{type(ocb.observer).__name__}-{device_id}] is created successfully.")
                else:
                    ocb = self._device_to_ocb_map[device_id]

                acb = ActionControlBlock(function=func, subordinate_plugin=config._env_stack[0], period=period)
                self._device_to_acb_map[device_id].append(acb)

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
        for acb in self._device_to_acb_map[obs.device_id]:

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
                    acb.function(data)
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

            # 将 observer 的 run 方法为改写为受控型
            old_run = _obs_class.run

            def _run(obs: Observer):
                while cls._observer_running_event.is_set():
                    old_run(obs)
                    # Observer 每观察一次会休眠 period 个时钟周期
                    time.sleep(obs.period * config.get("clock"))

            _obs_class.run = _run

            return _inner

        return _decorator

    def run(self):
        self._observer_running_event.set()

        for device_id, ocb in self._device_to_ocb_map.items():
            t = threading.Thread(name=f"{type(ocb.observer).__name__}-{ocb.observer.device_id}",
                                 target=ocb.observer.run, daemon=ocb.daemon)
            t.start()
            ocb.observer_status = ObserverStatus.RUNNING
            logger.info(f"@start-up Observer instance [{type(ocb.observer).__name__}-{device_id}] is working...")

        while True:
            if config.get("debug"):
                time.sleep(1)
            else:
                ans = input("是否结束程序？(Y/N)\n")
                if ans.upper() == "Y":
                    break
        self._observer_running_event.clear()

        logger.info(f"@shutdown main thread shutdown successfully.")


class Observer:
    """
    定义 Observer 的基类，该类负责将外部信息输入到本系统内部，当信息更新后，
    调用 agent 的 notify 进行, 同一 oid 只能创建一个实例。
    """

    def __init__(self, device_id: int, period: int = 5):
        """
        device_id：输入设备句柄/文件
        period：观察周期（每 period ms / 次）
        """
        self.device_id = device_id
        self.period = period
        self.agent = None

    def run(self, *args, **kwargs) -> None:
        """
        定义 Observer 的单次执行流程，切勿自行内置循环
        """
        raise NotImplementedError("请重载 run 方法。")


class ObserverStatus(enum.Enum):
    CREATE = 0
    RUNNING = 1
    TERMINATE = 2


@dataclass
class ObserverControlBlock:
    device_id: int
    observer: Observer
    observer_status: ObserverStatus = field(default=ObserverStatus.CREATE)
    daemon: bool = field(default=True)


@dataclass
class ActionControlBlock:
    function: Callable
    subordinate_plugin: str
    period: int = field(default=1)  # ms 作为单位
    clock_count: int = field(default=0)
    heavy: bool = field(default=False)
