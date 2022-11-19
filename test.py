import asyncio
import time

import mini_six as six
import cv2 as cv

from mini_six import look, DataSource, Image, SubscribeMode

six.init()


@look(DataSource.SCREENSHOT, 0x10010, period=20, subscribe_mode=SubscribeMode.PULL)
def action_1(image: Image):
    print("normal function 1 working:")
    time.sleep(5)


@look(DataSource.SCREENSHOT, 0x10010, period=20, subscribe_mode=SubscribeMode.PULL)
def action_2(image: Image):
    print("normal function 2 working:")
    time.sleep(5)


@look(DataSource.SCREENSHOT, 0x10010, period=20, subscribe_mode=SubscribeMode.CORO_PULL)
async def coro_action_1(image: Image):
    print("coro 1 working:")
    await asyncio.sleep(5)


@look(DataSource.SCREENSHOT, 0x10010, period=20, subscribe_mode=SubscribeMode.CORO_PULL)
async def coro_action_2(image: Image):
    print("coro 2 working:")
    await asyncio.sleep(5)


six.run()
